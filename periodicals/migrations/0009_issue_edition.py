# Generated by Django 2.0.3 on 2018-03-31 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('periodicals', '0008_issueedition'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='edition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='periodicals.IssueEdition'),
        ),
    ]
