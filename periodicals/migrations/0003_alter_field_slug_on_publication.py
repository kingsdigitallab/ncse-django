# Generated by Django 2.0.3 on 2018-03-14 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0002_alter_field_abbreviation_on_publication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='slug',
            field=models.SlugField(max_length=5, unique=True),
        ),
    ]
