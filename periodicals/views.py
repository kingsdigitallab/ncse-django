from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from haystack.generic_views import FacetedSearchView
from django.db.models import Max, Min
from .forms import PeriodicalsSearchForm
from .models import Article, Issue, Page, Publication


def _get_highlighted_words(request, page):
    # Words to highlight
    highlight_words = {}

    # Check if we need to do any highlighting
    if 'highlight' in request.GET:
        # Get the words to highlight
        words_to_highlight = request.GET['highlight'].split()
        page_words = page.words

        for word in words_to_highlight:
            try:
                highlight_words.update({word: page_words[word]})
            except KeyError:
                pass  # Not found

        return highlight_words
    else:
        return None


class ArticleDetailView(DetailView):
    template_name = 'periodicals/page_detail.html'
    context_object_name = 'article'
    queryset = Article.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        page = context['article'].page

        highlight_words = _get_highlighted_words(self.request, page)
        if highlight_words:
            context['highlight_words'] = highlight_words

        context['page'] = page

        return context

    def get_object(self):
        return get_object_or_404(
            Article, issue__slug=self.kwargs['issue_slug'],
            page__number=self.kwargs['number'],
            slug=self.kwargs['article_slug'])


class ArticlePrintView(TemplateView):
    template_name = 'periodicals/article_print.html'

    def get_context_data(self, **kwargs):
        context = super(ArticlePrintView, self).get_context_data(**kwargs)
        context['article'] = self.get_object()
        context['pages'] = context['article'].get_all_pages()

        return context

    def get_object(self):
        return get_object_or_404(
            Article, issue__slug=self.kwargs['issue_slug'],
            page__number=self.kwargs['number'],
            slug=self.kwargs['article_slug'])


class PageDetailView(DetailView):

    def get_object(self):
        return get_object_or_404(
            Page, issue__slug=self.kwargs['issue_slug'],
            number=self.kwargs['number'])

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        page = context['page']

        highlight_words = _get_highlighted_words(self.request, page)
        if highlight_words:
            context['highlight_words'] = highlight_words

        return context


class PagePrintView(TemplateView):
    template_name = 'periodicals/page_print.html'

    def get_object(self):
        return get_object_or_404(
            Page, issue__slug=self.kwargs['issue_slug'],
            number=self.kwargs['number'])

    def get_context_data(self, **kwargs):
        context = super(PagePrintView, self).get_context_data(**kwargs)
        context['page'] = self.get_object()

        return context


class IssueDetailView(DetailView):
    context_object_name = 'issue'
    queryset = Issue.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        return context


class PublicationDetailView(DetailView):
    context_object_name = 'publication'
    queryset = Publication.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PublicationDetailView, self).get_context_data(**kwargs)

        if 'year' in self.request.GET:
            year = self.request.GET['year']
        else:
            year = self.get_object().get_year_span()[0]

        issues = self.get_object().issues.filter(issue_date__year=year)

        context['selected_year'] = year
        context['selected_issues'] = issues

        return context


class PublicationIssueAjax(TemplateView):
    template_name = 'periodicals/ajax/issues_by_year.html'

    def get_context_data(self, **kwargs):
        context = super(PublicationIssueAjax, self).get_context_data(**kwargs)
        issues = Issue.objects.filter(
            publication__slug=self.kwargs['slug']).filter(
            issue_date__year=self.kwargs['year'])
        context['selected_issues'] = issues
        context['selected_year'] = self.kwargs['year']
        return context


class PublicationListView(ListView):
    context_object_name = 'publications'
    model = Publication


class PeriodicalsSearchView(FacetedSearchView):
    facet_fields = ['publication', 'category', 'year']
    form_class = PeriodicalsSearchForm
    template_name = 'periodicals/search.html'

    def get_initial(self):
        initial = super(FacetedSearchView, self).get_initial()
        # Find the first and last published years
        # set as default for the form
        first_issue = Issue.objects.all().aggregate(Min('issue_date'))
        first = first_issue['issue_date__min'].year
        last_issue = Issue.objects.all().aggregate(Max('issue_date'))
        last = last_issue['issue_date__max'].year
        initial['start_year'] = first
        initial['end_year'] = last
        return initial

    def get_context_data(self, **kwargs):
        context = super(PeriodicalsSearchView, self).get_context_data(**kwargs)
        request = self.request
        initial = self.get_initial()
        first_year = initial['start_year']
        last_year = initial['end_year']
        form = context['form']
        if 'selected_facets' in request.GET:
            context['selected_facets'] = request.GET.getlist('selected_facets')
            context['jumptoresults'] = True
        else:
            if form.is_bound and (('q' in form.cleaned_data and
                                   len(form.cleaned_data['q']) > 0) or (
                'start_year' in form.cleaned_data and
                form.cleaned_data['start_year'] is not None and
                int(form.cleaned_data['start_year']) >
                first_year) or (
                'end_year' in form.cleaned_data and
                form.cleaned_data['end_year'] is not None and
                int(form.cleaned_data[
                    'end_year']) < last_year
            )):
                context['jumptoresults'] = True
        context['form'] = form
        return context

    def get_queryset(self):
        queryset = super(PeriodicalsSearchView, self).get_queryset()

        for field in self.facet_fields:
            queryset = queryset.facet(
                field, sort='index', limit=-1, mincount=1)

        if 'order_by' in self.request.GET:
            order_by = self.request.GET['order_by']
            queryset = queryset.order_by(order_by, 'page_number',
                                         'position_in_page')

        return queryset
