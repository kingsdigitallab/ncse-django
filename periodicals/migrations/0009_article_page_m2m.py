# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-21 13:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0008_remove_page_from_article'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['aid']},
        ),
        migrations.AddField(
            model_name='article',
            name='page',
            field=models.ManyToManyField(to='periodicals.Page'),
        ),
    ]
