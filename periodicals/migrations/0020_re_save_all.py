# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    def resave(apps, schema_editor):

        print("WARNING: Re-saving all objects to generate\
              statistics and cached titles. This may take\
              a while.")
        Article = apps.get_model('periodicals', 'Article')
        Issue = apps.get_model('periodicals', 'Issue')
        Publication = apps.get_model('periodicals', 'Publication')

        for a in Article.objects.all():
            a.save()

        # Just in case
        for i in Issue.objects.all():
            i.save()

        for p in Publication.objects.all():
            p.save()


    dependencies = [
        ('periodicals', '0019_change_meta_options_on_article_issue_page'),
    ]

    operations = [
        migrations.RunPython(resave),
    ]
