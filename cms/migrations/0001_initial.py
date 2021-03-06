# Generated by Django 2.0.3 on 2018-03-12 12:24

import cms.models.streamfield
from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock())), icon='image', label='Aligned image')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML'))))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='IndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock())), icon='image', label='Aligned image')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML'))))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='RichTextPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('intro', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('pullquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()), ('affiliation', wagtail.core.blocks.CharBlock(required=False)), ('style', cms.models.streamfield.PullQuoteStyleChoiceBlock())), icon='openquote')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', cms.models.streamfield.ImageFormatChoiceBlock())), icon='image', label='Aligned image')), ('document', wagtail.documents.blocks.DocumentChooserBlock(icon='doc-full-inverse')), ('link', wagtail.core.blocks.StructBlock((('url', wagtail.core.blocks.CharBlock(required=False)), ('page', wagtail.core.blocks.PageChooserBlock(required=False)), ('label', wagtail.core.blocks.CharBlock()), ('style', cms.models.streamfield.LinkStyleChoiceBlock())), icon='link')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('html', wagtail.core.blocks.StructBlock((('html', wagtail.core.blocks.RawHTMLBlock()), ('alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())), icon='code', label='Raw HTML'))))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
    ]
