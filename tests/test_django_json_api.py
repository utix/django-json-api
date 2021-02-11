from django_json_api import __version__ as django_json_api_version


def test_version() -> None:
    assert django_json_api_version == "0.1.0"
