from django.urls import path

from .views import (ArticleDetailView, ArticlePrintView, IssueDetailView,
                    PageDetailView, PagePrintView, PeriodicalsSearchView,
                    PublicationDetailView, PublicationIssueAjax,
                    PublicationListView)

urlpatterns = [
    path('search/', PeriodicalsSearchView.as_view(), name='search'),
    path(('<slug:publication_slug>/'
          'issues/<slug:issue_slug>/'
          'page/<int:number>/'
          'articles/<slug:article_slug>/'),
         ArticleDetailView.as_view(), name='article-detail'),
    path(('<slug:publication_slug>/'
          'issues/<slug:issue_slug>/'
          'page/<int:number>/'
          'articles/<slug:article_slug>/print/'),
         ArticlePrintView.as_view(), name='article-print'),
    path(('<slug:publication_slug>/'
          'issues/<slug:issue_slug>/'
          'page/<int:number>/'),
         PageDetailView.as_view(), name='page-detail'),
    path(('<slug:publication_slug>/'
          'issues/<slug:issue_slug>/'
          'page/<int:number>/print/'),
         PagePrintView.as_view(), name='page-print'),
    path('<slug:publication_slug>/issues/<slug:slug>/',
         IssueDetailView.as_view(), name='issue-detail'),
    path('<slug:slug>/',
         PublicationDetailView.as_view(), name='publication-detail'),
    path('<slug:slug>/<int:year>/',
         PublicationIssueAjax.as_view(), name='publication-issue-ajax'),
    path('', PublicationListView.as_view(), name='publication-list')
]
