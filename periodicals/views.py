from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404
from haystack.generic_views import FacetedSearchView

from .forms import PeriodicalsSearchForm
from .models import Article, Issue, Page, Publication


class ArticleDetailView(DetailView):
    context_object_name = 'article'
    queryset = Article.objects.all()


class PageDetailView(DetailView):

    def get_object(self):
        return get_object_or_404(
            Page, issue__slug=self.kwargs['issue_slug'],
            number=self.kwargs['number'])

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        page = context['page']

        # Words to highlight
        highlight_words = {}

        # Check if we need to do any highlighting
        if 'highlight' in self.request.GET:
            # Get the words to highlight
            words_to_highlight = self.request.GET['highlight'].split()
            page_words = page.words

            for word in words_to_highlight:
                try:
                    highlight_words.update({word: page_words[word]})
                except KeyError:
                    pass  # Not found

        # Set all of the things
        if highlight_words:
            context['highlight_words'] = highlight_words

        return context


class IssueDetailView(DetailView):
    context_object_name = 'issue'
    queryset = Issue.objects.all()


class PublicationDetailView(DetailView):
    context_object_name = 'publication'
    queryset = Publication.objects.all()


class PublicationListView(ListView):
    context_object_name = 'publications'
    model = Publication


class PeriodicalsSearchView(FacetedSearchView):
    facet_fields = ['publication_abbreviation', 'issue_year']
    form_class = PeriodicalsSearchForm
    template_name = 'periodicals/search.html'

    def get_queryset(self):
        queryset = super(FacetedSearchView, self).get_queryset()

        for field in self.facet_fields:
            queryset = queryset.facet(
                field, sort='index', limit=-1, mincount=1)

        if 'order_by' in self.request.GET:
            order_by = self.request.GET['order_by']
            queryset = queryset.order_by(order_by)

        return queryset
