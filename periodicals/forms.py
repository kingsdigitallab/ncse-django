from django import forms
from django.forms.widgets import RadioSelect
from haystack.forms import FacetedSearchForm


class PeriodicalsSearchForm(FacetedSearchForm):

    MODE_DEFAULT = ('or', 'Any word')
    MODE_AND = ('and', 'All words')
    MODE_PHRASE = ('phrase', 'Phrase')
    MODE_CHOICES = (MODE_DEFAULT, MODE_AND, MODE_PHRASE)
    mode = forms.ChoiceField(
        choices=MODE_CHOICES, initial=MODE_DEFAULT[0], widget=RadioSelect)

    start_year = forms.IntegerField(required=False, initial=1793)
    end_year = forms.IntegerField(required=False, initial=1906)

    ORDER_BY_DEFAULT = ('issue_date', 'Date')
    ORDER_BY_TITLE = ('title', 'Title')
    ORDER_BY_RELEVANCE = ('score', 'Relevance')
    ORDER_BY_CHOICES = (ORDER_BY_DEFAULT, ORDER_BY_TITLE, ORDER_BY_RELEVANCE)
    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES, initial=ORDER_BY_DEFAULT[0],
        widget=RadioSelect)

    def no_query_found(self):
        return self.searchqueryset.all()

    def search(self):
        sqs = super(PeriodicalsSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['mode'] and self.cleaned_data['q']:
            mode = self.cleaned_data['mode']
            query = self.cleaned_data['q']

            if mode == self.MODE_DEFAULT[0]:
                words = query.split()
                for word in words:
                    sqs = sqs.filter_or(content=word)
            elif mode == self.MODE_AND[0]:
                words = query.split()
                for word in words:
                    sqs = sqs.filter(content=word)
            elif mode == self.MODE_PHRASE[0]:
                sqs = sqs.filter(content__exact=self.cleaned_data['q'])

        if self.cleaned_data['start_year']:
            sqs = sqs.filter(issue_year__gte=self.cleaned_data['start_year'])

        if self.cleaned_data['end_year']:
            sqs = sqs.filter(issue_year__lte=self.cleaned_data['end_year'])

        return sqs
