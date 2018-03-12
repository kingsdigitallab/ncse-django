from .base import *  # noqa

CACHE_REDIS_DATABASE = '1'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE

INTERNAL_IPS = INTERNAL_IPS + ['']
ALLOWED_HOSTS = ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_ncse_stg',
        'USER': 'app_ncse',
        'PASSWORD': '',
        'HOST': ''
    },
}

HAYSTACK_CONNECTIONS['default']['URL'] = 'http://localhost:8983/solr/stg'
