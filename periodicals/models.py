from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Publication(models.Model):
    abbreviation = models.CharField(max_length=3, unique=True)
    slug = models.SlugField(max_length=3, unique=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return '{}'.format(self.title if self.title else self.abbreviation)

    @property
    def url(self):
        return reverse(
            'publication-detail', kwargs={
                'slug': self.slug
            })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.abbreviation)
        super(Publication, self).save(*args, **kwargs)


class Issue(models.Model):
    publication = models.ForeignKey(Publication, related_name='issues')
    uid = models.CharField(max_length=32, unique=True)
    slug = models.CharField(max_length=32, unique=True)
    issue_date = models.DateField()
    number_of_pages = models.PositiveIntegerField(blank=True, null=True)
    pdf = models.FileField(upload_to='periodicals/', null=True)

    class Meta:
        ordering = ['publication', 'issue_date']

    def __str__(self):
        return '{}: {}'.format(self.publication, self.issue_date)

    @property
    def articles(self):
        return self.articles_in_issue.filter(continuation_from=None)

    @property
    def url(self):
        return reverse(
            'issue-detail', kwargs={
                'publication_slug': self.publication.slug,
                'slug': self.slug
            })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.uid)
        super(Issue, self).save(*args, **kwargs)


class Page(models.Model):
    height = models.PositiveIntegerField(null=True)
    issue = models.ForeignKey(Issue, related_name='pages')
    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='periodicals/')
    width = models.PositiveIntegerField(null=True)
    words = JSONField(default='{}', null="true")

    class Meta:
        ordering = ['issue', 'number']

    def __str__(self):
        return '{}: {}'.format(self.issue, self.number)

    @property
    def articles(self):
        return self.articles_in_page.all()

    @property
    def number_of_articles(self):
        return self.articles.count()

    @property
    def url(self):
        return reverse(
            'page-detail', kwargs={
                'publication_slug': self.issue.publication.slug,
                'issue_slug': self.issue.slug, 'number': self.number
            })

    def previous_page(self):
        if self.number > 1:
            return self.issue.pages.all()[self.number - 2]
        else:
            return None

    def next_page(self):
        if self.issue.number_of_pages > self.number:
            return self.issue.pages.all()[self.number]
        else:
            return None


class ArticleType(models.Model):
    title = models.CharField(max_length=512, blank=False, null=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Article(models.Model):
    issue = models.ForeignKey(Issue, related_name='articles_in_issue')
    page = models.ForeignKey(Page, blank=True, null=True,
                             related_name='articles_in_page')
    aid = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, null=True)
    position_in_page = models.PositiveIntegerField(blank=True, null=True)
    title = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_html = models.TextField(blank=True, null=True)
    continuation_from = models.ForeignKey(
        'self', blank=True, null=True, related_name='continued_from')
    continuation_to = models.ForeignKey(
        'self', blank=True, null=True, related_name='continues_in')
    bounding_box = JSONField(default='{}')
    title_image = models.ImageField(upload_to='periodicals/',
                                    blank=True, null=True)
    article_type = models.ForeignKey(ArticleType, blank=True, null=True)

    class Meta:
        ordering = ['page__number', 'position_in_page', 'aid']

    def __str__(self):
        return self.title if self.title else self.aid

    @property
    def url(self):
        return reverse(
            'article-detail', kwargs={
                'publication_slug': self.issue.publication.slug,
                'issue_slug': self.issue.slug, 'number': self.page.number,
                'article_slug': self.slug
            })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.aid)
        super(Article, self).save(*args, **kwargs)

    def get_text(self):
        if self.continuation_to:
            return '{} {}'.format(
                self.content if self.content else '',
                self.continuation_to.get_text())

        return self.content
