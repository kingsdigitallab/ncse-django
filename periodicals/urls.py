from django.conf.urls import include, url

from .views import (ArticleDetailView, IssueDetailView,
                    PageDetailView, PublicationDetailView,
                    PublicationListView)

urlpatterns = [
    url(r'^articles/', include('haystack.urls'), name='search'),
    url(r'^articles/(?P<pk>[0-9]+)/$',
        ArticleDetailView.as_view(), name='article-detail'),
    url(r'^page/(?P<pk>[0-9]+)/$',
        PageDetailView.as_view(), name='page-detail'),
    url(r'^issues/(?P<pk>[0-9]+)/$',
        IssueDetailView.as_view(), name='issue-detail'),
    url(r'^publications/(?P<pk>[0-9]+)/$',
        PublicationDetailView.as_view(), name='publication-detail'),
    url(r'^search/', include('haystack.urls'), name='search'),
    url(r'', PublicationListView.as_view(), name='publication-list')
]
