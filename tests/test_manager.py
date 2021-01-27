from urllib.parse import urlencode

from requests_mock.mocker import Mocker
import pytest

from django.core.cache import cache

from swlibs.json_api.manager import JSONAPIManager

from tests.swlibs.json_api.models import Dummy


# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument


PAGES = [
    {
        'data': [
            {
                'id': str(10 * j + i + 1),
                'type': 'tests',
                'attributes': {
                    'name': f'Record #{10 * j + i + 1}',
                },
            }
            for i in range(0, 10)
        ],
        'links': {
            'next': None if j == 4 else 'http://next'
        }
    }
    for j in range(0, 5)
]


@pytest.fixture
def pages():
    with Mocker() as mocker:
        for i, page in enumerate(PAGES):
            params = {
                'include': 'related',
                'fields[tests]': 'field,related',
                'page[size]': 10,
                'page[number]': i + 1,
            }
            mocker.register_uri(
                'GET',
                f'http://test/api/tests/?{urlencode(params)}',
                status_code=200,
                json=page,
            )
        yield mocker


def test_jsonapi_manager_sort():
    manager = JSONAPIManager(Dummy)
    manager_with_sort = manager.sort('field1', 'field2')
    manager_with_extended_sort = manager_with_sort.sort('field3')
    assert manager._sort == []
    assert manager_with_sort._sort == ['field1', 'field2']
    assert manager_with_extended_sort._sort == ['field1', 'field2', 'field3']


def test_jsonapi_manager_fields():
    manager = JSONAPIManager(Dummy)
    manager_with_fields = manager.fields(related=['field1', 'field2'])
    manager_with_extended_fields = manager_with_fields.fields(other=['field1'])
    assert manager._fields == {}
    assert manager_with_fields._fields == {'related': ['field1', 'field2']}
    assert manager_with_extended_fields._fields == {
        'related': ['field1', 'field2'], 'other': ['field1']}


def test_jsonapi_manager_include():
    manager = JSONAPIManager(Dummy)
    manager_with_include = manager.include('related1', 'related2')
    manager_with_extended_include = manager_with_include.include('related3')
    assert manager._include == []
    assert manager_with_include._include == ['related1', 'related2']
    assert manager_with_extended_include._include == ['related1', 'related2', 'related3']


def test_jsonapi_manager_filter():
    manager = JSONAPIManager(Dummy)
    manager_with_filters = manager.filter(pk=42)
    manager_with_extended_filters = manager_with_filters.filter(name='Test')
    assert manager._filters == {}
    assert manager_with_filters._filters == {'pk': 42}
    assert manager_with_extended_filters._filters == {'pk': 42, 'name': 'Test'}


def test_jsonapi_manager_iterator(pages):
    manager = JSONAPIManager(Dummy)
    records = list(manager.iterator())
    assert len(records) == 50
    assert all(map(lambda x: isinstance(x, Dummy), records))
    assert list(map(lambda x: x.id, records)) == list(range(1, 51))


def test_jsonapi_manager_iterator_with_included():
    cache.clear()
    page = {
        'data': [
            {
                'id': '137',
                'type': 'tests',
                'attributes': {}
            },
        ],
        'included': [
            {
                'id': '42',
                'type': 'tests',
                'attributes': {
                    'field': 'Included Record',
                }
            }
        ]
    }
    with Mocker() as mocker:
        params = {
            'include': 'related',
            'fields[tests]': 'field,related',
            'page[size]': 10,
            'page[number]': 1,
        }
        mocker.register_uri(
            'GET',
            f'http://test/api/tests/?{urlencode(params)}',
            status_code=200,
            json=page,
        )
        manager = JSONAPIManager(Dummy)
        list(manager.iterator())
    assert cache.get('jsonapi:tests:42').field == 'Included Record'


def test_jsonapi_manager_all(pages):
    manager = JSONAPIManager(Dummy)
    records = list(manager.all())
    assert len(records) == 50
    assert manager._cache == records
    pages.reset_mock()
    assert manager.all() == records
    assert not pages.called


def test_jsonapi_manager_count():
    params = {
        'page[size]': 1,
        'filter[key]': 'value',
    }
    with Mocker() as mocker:
        url = f'http://test/api/tests/?{urlencode(params)}'
        mocker.register_uri(
            'GET',
            url,
            status_code=200,
            json={
                'meta': {
                    'record_count': 137,
                }
            },
        )
        manager = JSONAPIManager(Dummy)
        assert manager.filter(key='value').count() == 137


def test_jsonapi_manager_getitem(pages):
    manager = JSONAPIManager(Dummy)
    assert manager[5].pk == 6


def test_jsonapi_manager_iter(pages):
    manager = JSONAPIManager(Dummy)
    assert len(list(iter(manager))) == 50
    assert manager._cache


def test_jsonapi_manager_get():
    cache.clear()
    document = {
        'data': {
            'id': '12',
            'type': 'tests',
            'attributes': {}
        },
        'included': [
            {
                'id': '137',
                'type': 'tests',
                'attributes': {'field': 'Included Record'},
            }
        ]
    }

    with Mocker() as mocker:
        params = {
            'fields[tests]': 'field,related',
            'include': 'related',
        }
        url = f'http://test/api/tests/12/?{urlencode(params)}'
        mocker.register_uri(
            'GET',
            url,
            status_code=200,
            json=document,
        )
        manager = JSONAPIManager(Dummy)
        record = manager.get(pk=12)
        # Verify API call and result
        assert record.id == 12
        assert mocker.called
        assert mocker.last_request.url == url
        # Loads included in cache
        assert cache.get('jsonapi:tests:137').field == 'Included Record'
        # Uses cache
        mocker.reset_mock()
        assert manager.get(pk=12) == record
        assert not mocker.called
        # Ignore cache
        assert manager.get(pk=12, ignore_cache=True) == record
        assert mocker.called
