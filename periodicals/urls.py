from django.urls import path

from .views import (ArticleDetailView, ArticlePrintView, IssueDetailView,
                    PageDetailView, PagePrintView, PeriodicalsSearchView,
                    PublicationDetailView, PublicationIssueAjax,
                    PublicationListView)

urlpatterns = [
    path('search/', PeriodicalsSearchView.as_view(), name='search'),
    path(('(?P<publication_slug>[-\w]+)/'
          'issues/(?P<issue_slug>[-\w]+)/'
          'page/(?P<number>[0-9]+)/'
          'articles/(?P<article_slug>[-\w]+)/$'),
         ArticleDetailView.as_view(), name='article-detail'),
    path(('(?P<publication_slug>[-\w]+)/'
          'issues/(?P<issue_slug>[-\w]+)/'
          'page/(?P<number>[0-9]+)/'
          'articles/(?P<article_slug>[-\w]+)/print/$'),
         ArticlePrintView.as_view(), name='article-print'),
    path(('(?P<publication_slug>[-\w]+)/'
          'issues/(?P<issue_slug>[-\w]+)/'
          'page/(?P<number>[0-9]+)/$'),
         PageDetailView.as_view(), name='page-detail'),
    path(('(?P<publication_slug>[-\w]+)/'
          'issues/(?P<issue_slug>[-\w]+)/'
          'page/(?P<number>[0-9]+)/print/$'),
         PagePrintView.as_view(), name='page-print'),
    path('(?P<publication_slug>[-\w]+)/issues/(?P<slug>[-\w]+)/$',
         IssueDetailView.as_view(), name='issue-detail'),
    path('(?P<slug>[-\w]+)/$',
         PublicationDetailView.as_view(), name='publication-detail'),
    path('(?P<slug>[-\w]+)/(?P<year>[-\w]+)/$',
         PublicationIssueAjax.as_view(), name='publication-issue-ajax'),
    path('$', PublicationListView.as_view(), name='publication-list')
]
