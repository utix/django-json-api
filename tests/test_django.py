from unittest import mock

import pytest

from django.test import TestCase

from swlibs.json_api.django import prefetch_jsonapi, WithJSONApiManager

from tests.swlibs.json_api.models import DummyModel, DummyRelated


class RelatedJSONAPIFieldTestCase(TestCase):
    def setUp(self):
        super().setUp()
        DummyRelated(pk=42).cache()
        DummyRelated(pk=137).cache()
        DummyRelated(pk=12).cache()

    def test_create_record_with_related_id(self):
        record = DummyModel.objects.create(related_id=42)
        record.refresh_from_db()
        self.assertEqual(record.related_id, 42)
        self.assertEqual(record.related, DummyRelated.objects.get(pk=42))

    def test_related_id_is_none(self):
        record = DummyModel()
        self.assertIsNone(record.related_id)
        self.assertIsNone(record.related)

    def test_assign_to_bad_type_value(self):
        record = DummyModel()
        expected = (
            'Cannot assign 42: '
            'DummyModel.related must be a DummyRelated instance'
        )
        with self.assertRaisesMessage(ValueError, expected):
            record.related = 42

    def test_assign_to_value_without_pk(self):
        record = DummyModel()
        expected = 'Cannot assign DummyRelated without pk to DummyModel.related'
        with self.assertRaisesMessage(ValueError, expected):
            record.related = DummyRelated()

    def test_init_with_related_none(self):
        record = DummyModel(related=DummyRelated(pk=42))
        self.assertEqual(record.related_id, 42)
        self.assertEqual(record.related, DummyRelated(pk=42))


@pytest.mark.django_db
def test_prefetch_jsonapi():
    # pylint: disable=no-member,protected-access
    _get_many = DummyRelated.get_many
    DummyRelated.get_many = mock.Mock()
    DummyRelated.get_many.return_value = {
        12: DummyRelated(pk=12),
        137: DummyRelated(pk=137),
        42: DummyRelated(pk=42),
    }
    instances = [
        DummyModel(pk=12, related_id=137, other_id=12),
        DummyModel(pk=13, related_id=42, other_id=None),
    ]
    prefetch_jsonapi(instances, {'other': DummyRelated, 'related': DummyRelated})
    assert instances[0]._cache_other == DummyRelated(pk=12)
    assert instances[0]._cache_related == DummyRelated(pk=137)
    assert instances[1]._cache_other is None
    assert instances[1]._cache_related == DummyRelated(pk=42)
    DummyRelated.get_many.assert_called_once()
    DummyRelated.get_many = _get_many


@pytest.mark.django_db
def test_with_jsonapi_manager():
    with mock.patch('swlibs.json_api.django.prefetch_jsonapi') as prefetch_jsonapi_mock:
        related = DummyRelated(pk=12).cache()
        instance = DummyModel.objects.create(pk=42, related=related)
        manager = WithJSONApiManager()
        manager.model = DummyModel
        qset = manager.filter(id__gt=12).prefetch_jsonapi(
            'related').prefetch_jsonapi('other').all()
        assert list(qset) == [instance]
        prefetch_jsonapi_mock.assert_called_once_with(
            [instance],
            {
                'related': DummyRelated,
                'other': DummyRelated,
            })
