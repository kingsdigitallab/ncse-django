# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-18 12:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0004_article_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='description',
        ),
    ]
