# Generated by Django 2.0.4 on 2018-06-21 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0021_publication_article_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='label',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]