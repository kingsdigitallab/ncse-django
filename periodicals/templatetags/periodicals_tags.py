import datetime

from django import template
from django.conf import settings

from periodicals.models import Issue, Publication
from ..forms import PeriodicalsSearchForm

register = template.Library()


@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)


@register.filter
def get_keys(value):
    return ','.join([key.split(':')[0] for key in value])


@register.filter
def split(value, arg):
    return value.split(arg)


@register.simple_tag
def initial_search_parameters():
    form = PeriodicalsSearchForm()
    params = ''

    for key, value in form.fields.items():
        if value.initial:
            params = '{}&{}='.format(params, key)
            params = '{}{}'.format(params, value.initial)

    return params


@register.filter
def get_issues_by_year(publication, year):
    return publication.get_issues.filter(issue_date__year=year)


@register.filter
def get_first_issues_by_year(publication, year):
    return publication.get_first_issues.filter(issue_date__year=year)


@register.simple_tag
def thumbnail(url):
    if hasattr(settings, 'IMAGE_SERVER_URL') and\
            hasattr(settings, 'IMAGE_SERVER_THUMBNAIL'):
        return '{}/{}/{}'.format(
            settings.IMAGE_SERVER_URL,
            url,
            settings.IMAGE_SERVER_THUMBNAIL)
    else:
        return url


@register.simple_tag(takes_context=True)
def get_selected_facets(context, exclude=None):
    """ Return any selected facets excluding exclude"""
    if 'selected_facets' in context:
        facets = context['selected_facets']
        if exclude:
            facets.remove(exclude)
        if len(facets) == 0:
            return None
        return facets
    return None


# Borrowed from wagtailbase
@register.simple_tag(takes_context=True)
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
    issues = Issue.objects.filter(
        issue_date__day=now.day,
        issue_date__month=now.month).order_by('?')[:3]
    return {'issues': issues}


@register.inclusion_tag('periodicals/includes/issue_gallery.html')
def get_issues_published_this_month():
    """  Get all issues published on same day as current month """
    now = datetime.datetime.now()
    issues = Issue.objects.filter(
        issue_date__month=now.month).order_by('?')[:3]
    return {'issues': issues}


@register.inclusion_tag('periodicals/includes/quick_search.html')
def quick_periodical_search_form():
    """ Add quick search with keyword only to periodical form"""
    form = PeriodicalsSearchForm(data={'order_by': "issue_date",
                                       'mode': 'or'
                                       })
    return {'form': form}


@register.inclusion_tag('periodicals/includes/publications.html')
def get_publications():
    return {'publications': Publication.objects.all()}
