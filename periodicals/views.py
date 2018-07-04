from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import View
from haystack.generic_views import FacetedSearchView
from django.db.models import Max, Min
from .forms import PeriodicalsSearchForm
from .models import Article, Issue, Page, Publication
from django.http import HttpResponse, HttpResponseRedirect
import re


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

        context['search_path'] = self.request.session.get('search_path')

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


class AjaxGalleryFirstEditionsByYear(TemplateView):
    template_name = ('periodicals/ajax/'
                     'issue_gallery_first_editions_by_year.html')

    def get_context_data(self, **kwargs):
        context = super(AjaxGalleryFirstEditionsByYear,
                        self).get_context_data(**kwargs)

        issues = Issue.objects.filter(
            publication__slug=self.kwargs['slug']).filter(
            issue_date__year=self.kwargs['year']).filter(
            edition=1)
        context['issues'] = issues
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

        # Here we save the url for use in going back to the search form
        request.session['search_path'] = request.get_full_path()

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


class XmodRedirectView(View):

    publication_map = {
        'MRUC': 'MRUC',
        'NS': 'NS',
        'NSS': 'NS',
        'LDR': 'L',
        'CLD': 'L',
        'EWJ': 'EWJ',
        'TTW': 'T',
        'TEC': 'PC',
        'MRP': 'MRUC',
    }

    def get(self, request, *args, **kwargs):
        if 'href' in request.GET and 'view' in request.GET:

            # Get URL params and rationalise them
            href = request.GET['href'].split('/')
            view = request.GET['view']

            publication = href[0]
            edition = None
            year = href[1]
            month = href[2]
            day = href[3]
            article_id = None
            page = None

            if 'entityid' in request.GET:
                article_id = request.GET['entityid']

            if 'page' in request.GET:
                page = request.GET['page']

            # Check for issue in publication label (e.g. NS2)
            if self._has_number(publication):
                splitter = re.match(r"(?P<pub>[a-zA-Z]+)(?P<ed>.+)$",
                                    publication)

                publication = splitter.group('pub')
                edition = splitter.group('ed')

            publication = self.publication_map[publication]

            # Let's get our bits
            issues = Issue.objects.filter(
                publication__slug__iexact=publication,
                issue_date__year=year,
                issue_date__month=month,
                issue_date__day=day
            )

            if edition:
                issues = issues.filter(edition=edition)

            if issues.exists():
                # Yay
                issue = issues[0]

                if view == 'entity' and article_id:
                    # Need to get a specific article:
                    articles = issue.articles_in_issue.filter(
                        aid__iexact=article_id)
                    if articles.exists():
                        return HttpResponseRedirect(articles[0].url)
                    else:
                        return HttpResponse(status=404)

                else:
                    if page:
                        # Specific page
                        pages = issue.pages.filter(number=page)
                        if pages.exists():
                            return HttpResponseRedirect(pages[0].url)
                        else:
                            return HttpResponse(status=404)
                    else:
                        # No page, go straight to issue
                        return HttpResponseRedirect(issue.url)

            else:
                return HttpResponse(status=404)

        else:
            # If we get to here, we've 404d as we don't have
            # enough URL params
            return HttpResponse(status=404)

    def _has_number(self, string):
        return re.search('\d', string)