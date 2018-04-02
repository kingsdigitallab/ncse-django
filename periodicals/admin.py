from django.contrib import admin

from .models import (Article, ArticleType, Issue, IssueComponent, IssueEdition,
                     Page, Publication)


class IssueInline(admin.TabularInline):
    model = Issue

    extra = 1
    show_change_link = True


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    inlines = [IssueInline]

    list_display = ['abbreviation', 'title']
    list_filter = ['abbreviation']


class PageInline(admin.TabularInline):
    model = Page

    extra = 1
    show_change_link = True


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    inlines = [PageInline]

    list_display = ['uid', 'publication',
                    'component', 'edition', 'edition_number', 'issue_date']
    list_filter = ['publication__abbreviation',
                   'component', 'edition', 'edition_number', 'issue_date']

    raw_id_fields = ['publication']


@admin.register(IssueComponent)
class IssueComponentAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(IssueEdition)
class IssueEditionAdmin(admin.ModelAdmin):
    list_display = ['title']


class ArticleInline(admin.TabularInline):
    model = Article

    extra = 1
    show_change_link = True


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['issue', 'number', 'image']

    list_filter = ['issue__publication']

    raw_id_fields = ['issue']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['aid', 'title', 'page', 'issue', 'publication']
    list_filter = ['issue']

    raw_id_fields = ['issue', 'page', 'continuation_from', 'continuation_to']


@admin.register(ArticleType)
class ArticleTypeAdmin(admin.ModelAdmin):
    list_display = ['title']
