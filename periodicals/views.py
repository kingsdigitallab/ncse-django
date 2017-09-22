from django.views.generic import DetailView, ListView

from .models import Article, Issue, Publication


class ArticleDetailView(DetailView):
    context_object_name = 'article'
    queryset = Article.objects.all()


class IssueDetailView(DetailView):
    context_object_name = 'issue'
    queryset = Issue.objects.all()


class PublicationDetailView(DetailView):
    context_object_name = 'publication'
    queryset = Publication.objects.all()


class PublicationListView(ListView):
    context_object_name = 'publications'
    model = Publication
