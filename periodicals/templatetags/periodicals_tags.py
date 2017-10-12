from django import template

from ..forms import PeriodicalsSearchForm

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
