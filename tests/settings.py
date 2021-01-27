import os

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.postgres',
    'psqlextra',
    'tests.apps.JSONAPITestonfig',
]


SERVICE = 'test'
ENVIRONMENT = 'test'
SECRET_KEY = 'rrrrrr-rrrrr-rrrrr-rrr'


DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'TEST': {
            'NAME': 'auto_tests',
        },
    },
}

