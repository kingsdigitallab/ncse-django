from django.views.generic import DetailView, ListView, TemplateView

from .models import Article, Issue, Page, Publication


class ArticleDetailView(DetailView):
    context_object_name = 'article'
    queryset = Article.objects.all()


class PageDetailView(TemplateView):
    template_name = 'periodicals/page_detail.html'
    page = None
    highlight_words = {}

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)

        # Get our page
        page_number = kwargs.get('pk', None)
        self.page = Page.objects.get(pk=page_number)

        # Check if we need to do any highlighting
        if 'highlight' in self.request.GET:
            # Get the words to highlight
            words_to_highlight = self.request.GET['highlight'].split()
            page_words = self.page.words

            for word in words_to_highlight:
                try:
                    self.highlight_words.update({word: page_words[word]})
                except KeyError:
                    pass  # Not found

        # Set all of the things
        if self.highlight_words:
            context['highlight_words'] = self.highlight_words
        context['page'] = self.page
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
