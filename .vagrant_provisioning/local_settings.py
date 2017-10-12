from .base import *  # noqa

DEBUG = True

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'mpol',
        'USER': 'mpol',
        'PASSWORD': 'mpol',
        'ADMINUSER': 'postgres',
        'HOST': 'localhost'
    },
}

# 10.0.2.2 is the default IP for the VirtualBox Host machine
INTERNAL_IPS = ['0.0.0.0', '127.0.0.1', '::1', '10.0.2.2']

SECRET_KEY = '12345'

FABRIC_USER = ''

# -----------------------------------------------------------------------------
# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
except ImportError:
    pass

# Change as required
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8983/solr/dev',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
    },
}

LOGGING['loggers']['periodicals'] = {}
LOGGING['loggers']['periodicals']['handlers'] = ['console']
LOGGING['loggers']['periodicals']['level'] = logging.DEBUG
