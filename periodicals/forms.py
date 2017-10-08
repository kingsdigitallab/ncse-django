from django import forms
from django.forms.widgets import RadioSelect
from haystack.forms import FacetedSearchForm


class PeriodicalsSearchForm(FacetedSearchForm):
    MODE_DEFAULT = 'or'
    MODE_AND = 'and'
    MODE_PHRASE = 'phrase'
    MODE_CHOICES = ((MODE_DEFAULT, 'Any word'),
                    (MODE_AND, 'All the words'),
                    (MODE_PHRASE, 'Phrase'))
    mode = forms.ChoiceField(choices=MODE_CHOICES,
                             initial=MODE_DEFAULT, widget=RadioSelect)
    start_year = forms.IntegerField(required=False)
    end_year = forms.IntegerField(required=False)

    def search(self):
        sqs = super(PeriodicalsSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['mode'] and self.cleaned_data['q']:
            mode = self.cleaned_data['mode']

            if mode == self.MODE_AND:
                sqs = sqs.filter_and(content=self.cleaned_data['q'])
            elif mode == self.MODE_PHRASE:
                sqs = sqs.filter(content__exact=self.cleaned_data['q'])

        if self.cleaned_data['start_year']:
            sqs = sqs.filter(issue_year__gte=self.cleaned_data['start_year'])

        if self.cleaned_data['end_year']:
            sqs = sqs.filter(issue_year__lte=self.cleaned_data['end_year'])

        return sqs
