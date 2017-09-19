from .base import *  # noqa

INTERNAL_IPS = INTERNAL_IPS + ['']
ALLOWED_HOSTS = ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_mpol_liv',
        'USER': 'app_mpol',
        'PASSWORD': '',
        'HOST': ''
    },
}

HAYSTACK_CONNECTIONS['default']['URL'] = 'http://localhost:8983/solr/liv'
