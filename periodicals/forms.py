from django import forms
from haystack.forms import FacetedSearchForm


class PeriodicalsSearchForm(FacetedSearchForm):
    start_year = forms.IntegerField(required=False)
    end_year = forms.IntegerField(required=False)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(PeriodicalsSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['start_year']:
            sqs = sqs.filter(issue_year__gte=self.cleaned_data['start_year'])

        if self.cleaned_data['end_year']:
            sqs = sqs.filter(issue_year__lte=self.cleaned_data['end_year'])

        return sqs
