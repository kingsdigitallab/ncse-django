# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify


def set_slug(apps, schema_editor):
    Publication = apps.get_model('periodicals', 'Publication')

    for obj in Publication.objects.all():
        obj.slug = slugify(obj.abbreviation)
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0019_publication_slug'),
    ]

    operations = [
        migrations.RunPython(set_slug, migrations.RunPython.noop)
    ]
