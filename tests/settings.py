INSTALLED_APPS = [
    "rest_framework",
    "tests.apps.JSONAPITestonfig",
]


SERVICE = "test"
ENVIRONMENT = "test"
SECRET_KEY = "rrrrrr-rrrrr-rrrrr-rrr"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "TEST": {
            "NAME": "auto_tests",
        },
    },
}
