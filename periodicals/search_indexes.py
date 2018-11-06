from haystack import indexes

from .models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    url = indexes.CharField(model_attr='url', indexed=False)
    aid = indexes.CharField(model_attr='aid', indexed=False)
    title = indexes.CharField(model_attr='title', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    category = indexes.FacetCharField(model_attr='article_type', null=True)
    image = indexes.CharField(model_attr='title_image', indexed=False)
    text = indexes.CharField(document=True, model_attr='content', null=True)
    slug = indexes.CharField(model_attr='slug', indexed=False)
    page = indexes.IntegerField(model_attr='page__id', indexed=False)
    position_in_page = indexes.IntegerField(
        model_attr='position_in_page', null=True)
    page_url = indexes.CharField(indexed=False, null=True)
    page_number = indexes.IntegerField(
        model_attr='page__number', indexed=False)
    page_image = indexes.CharField(model_attr='page__image', indexed=False)

    issue = indexes.IntegerField(model_attr='issue__id', indexed=False)
    issue_url = indexes.CharField(indexed=False, null=True)
    issue_uid = indexes.CharField(model_attr='issue__uid', indexed=False)
    issue_slug = indexes.CharField(model_attr='issue__slug', indexed=False)
    issue_date = indexes.FacetDateField(
        model_attr='issue__issue_date', null=True)
    issue_year = indexes.FacetIntegerField(
        model_attr='issue__issue_date__year', null=True)
    issue_number_of_pages = indexes.IntegerField(
        model_attr='issue__number_of_pages', indexed=False, null=True)
    issue_pdf = indexes.CharField(model_attr='issue__pdf', indexed=False)
    publication_url = indexes.CharField(indexed=False, null=True)
    publication_abbreviation = indexes.FacetCharField(
        model_attr='issue__publication__abbreviation', null=True)
    publication_slug = indexes.CharField(
        model_attr='issue__publication__slug', indexed=False)
    publication_title = indexes.FacetCharField(
        model_attr='issue__publication__title', null=True)
    publication_description = indexes.CharField(
        model_attr='issue__publication__description', null=True)

    # Prettier facets
    publication = indexes.FacetCharField(null=True)
    year = indexes.FacetIntegerField(
        model_attr='issue__issue_date__year', null=True)

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_page_url(self, obj):
        if obj.page:
            return obj.page.url
        else:
            return None

    def prepare_issue_url(self, obj):
        if obj.issue:
            return obj.issue.url
        else:
            return None

    def prepare_publication_url(self, obj):
        if obj.issue and obj.issue.publication:
            return obj.issue.publication.url
        else:
            return None

    def prepare_publication(self, obj):
        if obj.issue and obj.issue.publication:
            if obj.issue.publication.title:
                return obj.issue.publication.title
            else:
                return obj.issue.publication.abbreviation
        else:
            return None
