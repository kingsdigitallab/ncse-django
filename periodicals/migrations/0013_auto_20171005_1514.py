# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 14:14
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0012_article_bounding_box'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='words',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='{}', null='true'),
        ),
    ]
