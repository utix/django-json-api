from django.db.models import Model

from django_json_api import django, fields, models


class Dummy(models.JSONAPIModel):
    class Meta:
        resource_type = "tests"
        api_url = "http://test/api"
        page_size = 10

    field = fields.Attribute()
    related = fields.Relationship()


class DummyRelated(models.JSONAPIModel):
    class Meta:
        api_url = "http://example.com"
        resource_type = "related_records"

    name = fields.Attribute()
    other_related = fields.Relationship()


class DummyModel(Model):
    related = django.RelatedJSONAPIField(DummyRelated)
    other = django.RelatedJSONAPIField(DummyRelated, null=True)
