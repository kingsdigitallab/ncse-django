import datetime

from django import template

from periodicals.models import Issue
from ..forms import PeriodicalsSearchForm

register = template.Library()


@register.simple_tag
def initial_search_parameters():
    form = PeriodicalsSearchForm()
    params = ''

    for key, value in form.fields.items():
        if value.initial:
            params = '{}&{}='.format(params, key)
            params = '{}{}'.format(params, value.initial)

    return params


# Borrowed from wagtailbase
@register.assignment_tag(takes_context=True)
def get_request_parameters(context, exclude=None):
    """Returns a string with all the request parameters except the exclude
    parameter."""
    params = ''
    request = context['request']

    for key, value in request.GET.items():
        if key != exclude and len(value) > 0:
            params += '&{key}={value}'.format(key=key, value=value)
    if len(params) == 0:
        params = None
    return params


@register.inclusion_tag('periodicals/includes/issue_gallery.html')
def get_issues_published_today():
    """ Get all issues published on same day as current day"""
    now = datetime.datetime.now()
    issues = Issue.objects.filter(issue_date__day=now.day)
    return {'issues': issues}


@register.inclusion_tag('periodicals/includes/issue_gallery.html')
def get_issues_published_this_month():
    """  Get all issues published on same day as current month """
    now = datetime.datetime.now()
    issues = Issue.objects.filter(issue_date__month=now.month)[:3]
    return {'issues': issues}


@register.inclusion_tag('periodicals/includes/quick_search.html')
def quick_periodical_search_form():
    """ Add quick search with keyword only to periodical form"""
    form = PeriodicalsSearchForm(data={'order_by': "issue_date",
                                       'mode': 'or'
                                       })
    return {'form': form}
