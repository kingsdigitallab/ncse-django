# Generated by Django 2.0.4 on 2018-04-18 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0016_optimisation_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='article_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
