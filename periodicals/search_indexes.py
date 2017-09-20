from haystack import indexes

from .models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    aid = indexes.CharField(model_attr='aid', indexed=False)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    text = indexes.CharField(document=True, model_attr='content')

    page = indexes.IntegerField(model_attr='page__id', indexed=False)
    page_number = indexes.CharField(model_attr='page__number', indexed=False)
    page_image = indexes.CharField(model_attr='page__image', indexed=False)

    issue = indexes.IntegerField(model_attr='page__issue__id', indexed=False)
    issue_uid = indexes.CharField(model_attr='page__issue__uid', indexed=False)
    issue_date = indexes.FacetDateField(model_attr='page__issue__issue_date')
    issue_number_of_pages = indexes.IntegerField(
        model_attr='page__issue__number_of_pages', indexed=False)
    issue_pdf = indexes.CharField(model_attr='page__issue__pdf', indexed=False)

    publication = indexes.IntegerField(
        model_attr='page__issue__publication__id', indexed=False)
    publication_abbreviation = indexes.FacetCharField(
        model_attr='page__issue__publication__abbreviation')
    publication_title = indexes.FacetCharField(
        model_attr='page__issue__publication__title')
    publication_description = indexes.CharField(
        model_attr='page__issue__publication__description')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.all()