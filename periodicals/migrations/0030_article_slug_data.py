# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify


def set_slug(apps, schema_editor):
    Article = apps.get_model('periodicals', 'Article')

    for obj in Article.objects.all():
        obj.slug = slugify(obj.aid)
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0029_article_slug'),
    ]

    operations = [
        migrations.RunPython(set_slug, migrations.RunPython.noop)
    ]
