from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from kdl_ldap.signal_handlers import \
    register_signal_handlers as kdl_ldap_register_signal_hadlers

kdl_ldap_register_signal_hadlers()

admin.autodiscover()

urlpatterns = []

try:
    if settings.DEBUG:
        import debug_toolbar
        urlpatterns += [
            path(r'^__debug__/', include(debug_toolbar.urls)),
        ]
except ImportError:
    pass

urlpatterns += [
    path('admin/', include(admin.site.urls)),
    path('digger/', include('activecollab_digger.urls')),
    path('periodicals/', include('periodicals.urls')),

    path('wagtail/', include('wagtail.admin.urls')),
    path('documents/', include('wagtail.documents.urls')),
    path('', include('wagtail.core.urls')),
]

# -----------------------------------------------------------------------------
# Static file DEBUGGING
# -----------------------------------------------------------------------------
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import os.path

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL + 'images/',
                          document_root=os.path.join(settings.MEDIA_ROOT,
                                                     'images'))
