# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-13 12:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0028_add_article_type_to_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='slug',
            field=models.SlugField(max_length=32, null=True, unique=False),
            preserve_default=False,
        ),
    ]