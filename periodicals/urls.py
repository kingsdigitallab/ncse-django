from django.conf.urls import url

from .views import (ArticleDetailView, ArticlePrintView, IssueDetailView,
                    PageDetailView, PagePrintView,
                    PeriodicalsSearchView, PublicationDetailView,
                    PublicationListView)

urlpatterns = [
    url(r'^search/', PeriodicalsSearchView.as_view(), name='search'),
    url((r'^(?P<publication_slug>[-\w]+)/'
         'issues/(?P<issue_slug>[-\w]+)/'
         'page/(?P<number>[0-9]+)/'
         'articles/(?P<article_slug>[-\w]+)/$'),
        ArticleDetailView.as_view(), name='article-detail'),
    url((r'^(?P<publication_slug>[-\w]+)/'
         'issues/(?P<issue_slug>[-\w]+)/'
         'page/(?P<number>[0-9]+)/'
         'articles/(?P<article_slug>[-\w]+)/print/$'),
        ArticlePrintView.as_view(), name='article-print'),
    url((r'^(?P<publication_slug>[-\w]+)/'
         'issues/(?P<issue_slug>[-\w]+)/'
         'page/(?P<number>[0-9]+)/$'),
        PageDetailView.as_view(), name='page-detail'),
    url((r'^(?P<publication_slug>[-\w]+)/'
         'issues/(?P<issue_slug>[-\w]+)/'
         'page/(?P<number>[0-9]+)/print/$'),
        PagePrintView.as_view(), name='page-print'),
    url(r'^(?P<publication_slug>[-\w]+)/issues/(?P<slug>[-\w]+)/$',
        IssueDetailView.as_view(), name='issue-detail'),
    url(r'^(?P<slug>[-\w]+)/$',
        PublicationDetailView.as_view(), name='publication-detail'),
    url(r'', PublicationListView.as_view(), name='publication-list')
]
