from django.conf.urls import include, url
from .views import ArticleDetailView

urlpatterns = [
    url(r'^search/', include('haystack.urls'), name='search'),
    url(r'^articles/', include('haystack.urls'), name='search'),
    url(r'^articles/(?P<pk>[0-9]+)/$',
        ArticleDetailView.as_view(), name='article-detail'),
]
