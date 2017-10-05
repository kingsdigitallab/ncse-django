# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 11:38
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0010_related_names'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='pdf',
        ),
        migrations.RemoveField(
            model_name='page',
            name='pdf',
        ),
        migrations.AddField(
            model_name='page',
            name='words',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='{}'),
        ),
    ]