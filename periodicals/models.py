from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.text import slugify


class Publication(models.Model):
    abbreviation = models.CharField(max_length=3, unique=True)
    slug = models.SlugField(max_length=3, unique=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ordering = models.PositiveIntegerField(blank=True, null=True)
    title_image = models.ImageField(null=True, blank=True)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return '{}'.format(self.title if self.title else self.abbreviation)

    @property
    def url(self):
        return reverse(
            'publication-detail', kwargs={
                'slug': self.slug
            })

    def get_year_span(self):
        if self.issues.all().count() > 0:
            return [self.issues.first().issue_date.year,
                    self.issues.last().issue_date.year]

        return None

    def get_number_of_years(self):
        year_span = self.get_year_span()

        if year_span:
            return year_span[1] - year_span[0] + 1

        return None

    def get_total_number_of_pages(self):
        aggregation = self.issues.aggregate(total_pages=Sum('number_of_pages'))

        if aggregation:
            return aggregation['total_pages']

        return 0

    def save(self, *args, **kwargs):
        self.slug = slugify(self.abbreviation)
        if self.issues.all().count():
            self.ordering = self.issues.first().issue_date.year
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
        article = ArticleType.objects.get_or_create(title='Article')[0]
        return self.articles_in_issue.filter(continuation_from=None,
                                             article_type=article)

    @property
    def ads(self):
        ad = ArticleType.objects.get_or_create(title='Ad')[0]
        return self.articles_in_issue.filter(continuation_from=None,
                                             article_type=ad)

    @property
    def articles_and_ads(self):
        return (self.articles | self.ads).order_by('position_in_page')

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

    @property
    def print_url(self):
        return reverse(
            'page-print', kwargs={
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
    title = models.CharField(max_length=2048, blank=False, null=False)

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
    title = models.CharField(max_length=2048, blank=True, null=True)
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

    @property
    def print_url(self):
        return reverse(
            'article-print', kwargs={
                'publication_slug': self.issue.publication.slug,
                'issue_slug': self.issue.slug, 'number': self.page.number,
                'article_slug': self.slug
            })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.aid)
        super(Article, self).save(*args, **kwargs)

    # Gets all pages in the article (including those continued to/from)
    def get_all_pages(self):
        current_article = self

        while current_article.continuation_from:
            current_article = current_article.continuation_from

        pages = [current_article.page]
        while current_article.continuation_to:
            current_article = current_article.continuation_to
            if current_article.page not in pages:
                pages.append(current_article.page)

        return pages

    # Get total number of pages in article:
    def get_number_of_pages(self):
        return len(self.get_all_pages())

    # Gets the position of this page in a multi-page article
    # e.g. *1* of 5 (returns 1).
    def get_position_in_article(self):
        count = 1
        current_article = self

        while current_article.continuation_from:
            current_article = current_article.continuation_from
            count = count + 1

        return count

    def get_text(self):
        if self.continuation_to:
            return '{} {}'.format(
                self.content if self.content else '',
                self.continuation_to.get_text())

        return self.content

    def get_real_bounding_box(self):

        # Global variables
        page = self.page
        a = self.bounding_box  # Easier to read later on
        weight = 1.2  # Margin of error for wonky pages

        # Check if single article on page
        if page.number_of_articles == 1:
            return [
                {'x': a['x0'], 'y': a['y0']},
                {'x': a['x0'], 'y': a['y1']},
                {'x': a['x1'], 'y': a['y1']},
                {'x': a['x1'], 'y': a['y0']},
            ]
        else:
            # Article spans multiple columns
            page_articles = page.articles_in_page.order_by(
                'position_in_page').all()
            first_article = page_articles[0]
            last_article = page_articles[page.number_of_articles - 1]

            if self == first_article:
                next_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page + 1)

                # noqa here as single letter variables are nicer
                # when dealing with this
                l = next_article.bounding_box  # noqa

                if int(a['x1']) - int(a['x0']) > \
                   (int(l['x1']) - int(l['x0'])) * weight:
                    # Double column
                    return [
                        {'x': a['x0'], 'y': a['y0']},
                        {'x': a['x1'], 'y': a['y0']},
                        {'x': a['x1'], 'y': l['y0']},
                        {'x': l['x0'], 'y': l['y0']},
                        {'x': l['x0'], 'y': a['y1']},
                        {'x': a['x0'], 'y': a['y1']},
                    ]
                else:
                    # Single column
                    return [
                        {'x': a['x0'], 'y': a['y0']},
                        {'x': a['x0'], 'y': a['y1']},
                        {'x': a['x1'], 'y': a['y1']},
                        {'x': a['x1'], 'y': a['y0']}
                    ]
            elif self == last_article:
                # This is the last article on the page

                previous_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page - 1)
                f = previous_article.bounding_box

                if int(a['x1']) - int(a['x0']) > \
                   (int(f['x1']) - int(f['x0'])) * weight:
                    # Double column
                    return [
                        {'x': a['x0'], 'y': f['y1']},
                        {'x': f['x1'], 'y': f['y1']},
                        {'x': f['x1'], 'y': a['y0']},
                        {'x': a['x1'], 'y': a['y0']},
                        {'x': a['x1'], 'y': a['y1']},
                        {'x': a['x0'], 'y': a['y1']},

                    ]
                else:
                    # Single column
                    return [
                        {'x': a['x0'], 'y': a['y0']},
                        {'x': a['x0'], 'y': a['y1']},
                        {'x': a['x1'], 'y': a['y1']},
                        {'x': a['x1'], 'y': a['y0']}
                    ]
            else:
                previous_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page - 1)
                next_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page + 1)

                f = previous_article.bounding_box
                l = next_article.bounding_box  # noqa

                # Check if over single or double column
                if int(a['x1']) - int(a['x0']) > \
                   (int(f['x1']) - int(f['x0'])) * weight \
                   and int(a['x1']) - int(a['x0']) > \
                   (int(l['x1']) - int(l['x0'])) * weight:
                    # Double column
                    return [
                        {'x': a['x0'], 'y': f['y1']},
                        {'x': f['x1'], 'y': f['y1']},
                        {'x': f['x1'], 'y': a['y0']},
                        {'x': a['x1'], 'y': a['y0']},
                        {'x': a['x1'], 'y': l['y0']},
                        {'x': l['x0'], 'y': l['y0']},
                        {'x': l['x0'], 'y': a['y1']},
                        {'x': a['x0'], 'y': a['y1']}
                    ]
                else:
                    # Single column
                    return [
                        {'x': a['x0'], 'y': a['y0']},
                        {'x': a['x0'], 'y': a['y1']},
                        {'x': a['x1'], 'y': a['y1']},
                        {'x': a['x1'], 'y': a['y0']}
                    ]
