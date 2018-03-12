from .base import *  # noqa

CACHE_REDIS_DATABASE = '2'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE

DEBUG = True

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_mpol_dev',
        'USER': 'app_mpol',
        'PASSWORD': '',
        'HOST': ''
    },
}

LOGGING_LEVEL = logging.DEBUG

LOGGING['loggers']['mpol']['level'] = LOGGING_LEVEL

HAYSTACK_CONNECTIONS['default']['URL'] = 'http://localhost:8983/solr/dev'

# -----------------------------------------------------------------------------
# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar', ]
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
except ImportError:
    pass
