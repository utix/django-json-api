import os

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.postgres',
    'psqlextra',
    'tests.apps.JSONAPITestonfig',
]


SERVICE = 'test'
ENVIRONMENT = 'test'
SECRET_KEY = 'tagada-tsoin-tsoin-137'


DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',
        'NAME': 'postgres',
        'USER': 'vic',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'auto_tests',
        },
    },
}

