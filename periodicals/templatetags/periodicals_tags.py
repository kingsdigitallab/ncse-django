from django import template

from ..forms import PeriodicalsSearchForm
import datetime
from periodicals.models import Issue

register = template.Library()


@register.simple_tag
def initial_search_parameters():
    form = PeriodicalsSearchForm()
    params = ''

    for key, value in form.fields.items():
        params = '{}&{}='.format(params, key)

        if value.initial:
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
        if key != exclude:
            params += '&{key}={value}'.format(key=key, value=value)
    return params


# Get all issues published on same day as current day
@register.assignment_tag()
def get_issues_published_today():
    now = datetime.datetime.now()
    issues = Issue.objects.filter(issue_date__day=now.day)
    return issues


# Get all issues published on same day as current month
@register.assignment_tag()
def get_issues_published_this_month():
    now = datetime.datetime.now()
    issues = Issue.objects.filter(issue_date__month=now.month)
    return issues
