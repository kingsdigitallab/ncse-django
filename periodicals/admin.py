from django.contrib import admin

from .models import Article, Issue, Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['abbreviation', 'title']
    list_filter = ['abbreviation']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['uid', 'publication', 'issue_date']
    list_filter = ['publication__abbreviation', 'issue_date']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['issue', 'aid', 'title', 'page_number']
