from django.contrib.humanize.templatetags.humanize import ordinal
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.text import slugify


class Publication(models.Model):
    abbreviation = models.CharField(max_length=5)
    slug = models.SlugField(max_length=5)
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ordering = models.PositiveIntegerField(blank=True, null=True)
    title_image = models.ImageField(null=True, blank=True)
    year_from = models.PositiveIntegerField(blank=True, null=True)
    year_to = models.PositiveIntegerField(blank=True, null=True)
    page_count = models.PositiveIntegerField(default=0)
    issue_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']
        unique_together = ('abbreviation', 'slug', 'title')

    def __str__(self):
        return '{}'.format(self.title if self.title else self.abbreviation)

    @property
    def url(self):
        return reverse(
            'publication-detail', kwargs={
                'slug': self.slug
            })

    def get_year_span(self):
        return [self.year_from, self.year_to]

    def get_year_range(self):
        return range(self.year_from, self.year_to + 1)

    def get_number_of_years(self):
        if self.year_to and self.year_from:
            return (self.year_to - self.year_from) + 1
        else:
            return 0

    @property
    def get_issues(self):
        return Issue.objects.filter(publication=self)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.abbreviation)
        if self.issues.all().count():

            # Save issue count
            self.issue_count = self.issues.all().count()
            # Save ordering
            self.ordering = self.issues.first().issue_date.year

            # Save year span
            self.year_from = self.issues.first().issue_date.year
            self.year_to = self.issues.last().issue_date.year

            # Save page counts
            aggregation = self.issues.aggregate(
                total_pages=Sum('number_of_pages'))
            if aggregation:
                self.page_count = aggregation['total_pages']

        super(Publication, self).save(*args, **kwargs)


class IssueComponent(models.Model):
    title = models.CharField(
        max_length=256, blank=False, null=False, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Issue(models.Model):
    publication = models.ForeignKey(Publication, related_name='issues',
                                    on_delete=models.CASCADE)
    uid = models.CharField(max_length=32, unique=True)
    slug = models.CharField(max_length=32, unique=True)
    issue_date = models.DateField()
    component = models.ForeignKey(IssueComponent, blank=True, null=True,
                                  on_delete=models.CASCADE)
    edition = models.CharField(max_length=128, blank=True, null=True,)
    number_of_pages = models.PositiveIntegerField(blank=True, null=True)
    pdf = models.FileField(upload_to='periodicals/', null=True)
    article_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['issue_date', 'edition']

    def __str__(self):
        issue = '{}: {}'.format(self.publication, self.issue_date)

        if self.edition != 1:
            issue = '{}, {} edition'.format(issue, ordinal(self.edition))

        if self.component:
            issue = '{}, {}'.format(issue, self.component)

        return issue

    @property
    def departments(self):
        return self.get_base_query().filter(
            title_image__isnull=False).exclude(title_image__exact='').order_by(
            'page__number', 'position_in_page')

    @property
    def articles(self):
        article = ArticleType.objects.get_or_create(title='Article')[0]
        return self.get_base_query().filter(article_type=article)

    @property
    def ads(self):
        ad = ArticleType.objects.get_or_create(title='Ad')[0]
        return self.get_base_query().filter(article_type=ad)

    @property
    def items(self):
        return self.get_base_query()

    @property
    def pictures(self):
        picture = ArticleType.objects.get_or_create(title='Picture')[0]
        return self.get_base_query().filter(article_type=picture)

    @property
    def url(self):
        return reverse(
            'issue-detail', kwargs={
                'publication_slug': self.publication.slug,
                'slug': self.slug
            })

    def get_components(self):
        return self.publication.issues.filter(
            issue_date=self.issue_date, edition=self.edition).exclude(
                uid=self.uid)

    def get_editions(self):
        return self.publication.issues.filter(
            issue_date=self.issue_date).exclude(
            edition=self.edition).order_by('edition')

    def get_base_query(self):
        return self.articles_in_issue.select_related(
            'page').defer(
            'content', 'content_html', 'bounding_box', 'page__words').filter(
            continuation_from=None)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.uid)
        self.article_count = self.articles_in_issue.filter(
            continuation_from=None).count()

        # Resave publication!
        self.publication.save()
        super(Issue, self).save(*args, **kwargs)


class Page(models.Model):
    height = models.PositiveIntegerField(null=True)
    issue = models.ForeignKey(Issue, related_name='pages',
                              on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='periodicals/')
    width = models.PositiveIntegerField(null=True)
    words = JSONField(default='{}', null="true")
    article_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return '{}: {}'.format(self.issue, self.number)

    @property
    def departments(self):
        return self.get_base_query().filter(
            title_image__isnull=False).exclude(title_image__exact='').order_by(
            'position_in_page')

    @property
    def articles(self):
        article = ArticleType.objects.get_or_create(title='Article')[0]
        return self.get_base_query().filter(article_type=article)

    @property
    def ads(self):
        ad = ArticleType.objects.get_or_create(title='Ad')[0]
        return self.get_base_query().filter(article_type=ad)

    @property
    def items(self):
        return self.get_base_query()

    @property
    def pictures(self):
        picture = ArticleType.objects.get_or_create(title='Picture')[0]
        return self.get_base_query().filter(article_type=picture)

    @property
    def number_of_articles(self):
        return self.article_count

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

    def get_base_query(self):
        return Article.objects.filter(page=self).select_related(
            'page').defer(
            'content', 'content_html', 'bounding_box', 'page__words').filter(
            continuation_from=None)

    def save(self, *args, **kwargs):
        self.article_count = self.articles.count()
        self.issue.save()
        super(Page, self).save(*args, **kwargs)


class ArticleType(models.Model):
    title = models.CharField(max_length=2048, blank=False, null=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        if self.title == 'Article':
            return 'Text'
        else:
            return self.title


class Article(models.Model):
    issue = models.ForeignKey(Issue, related_name='articles_in_issue',
                              on_delete=models.CASCADE)
    page = models.ForeignKey(Page, blank=True, null=True,
                             related_name='articles_in_page',
                             on_delete=models.CASCADE)
    aid = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32, null=True)
    title = models.CharField(max_length=2048, blank=True, null=True)
    article_type = models.ForeignKey(ArticleType, blank=True, null=True,
                                     on_delete=models.CASCADE)
    title_image = models.ImageField(upload_to='periodicals/',
                                    blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    position_in_page = models.PositiveIntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_html = models.TextField(blank=True, null=True)
    continuation_from = models.ForeignKey(
        'self', blank=True, null=True, related_name='continued_from',
        on_delete=models.CASCADE)
    continuation_to = models.ForeignKey(
        'self', blank=True, null=True, related_name='continues_in',
        on_delete=models.CASCADE)
    bounding_box = JSONField(default='{}')

    class Meta:
        ordering = ['position_in_page', 'aid']

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

    @property
    def publication(self):
        return self.issue.publication

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
        current_article = self
        pages = []

        while current_article.continuation_from:
            if current_article.page not in pages:
                pages.append(current_article.page)
            current_article = current_article.continuation_from

        # Sanity check, for when current_article is a lone child
        pages.append(current_article.page)

        return len(pages)

    def get_text(self):
        if self.continuation_to:
            return '{} {}'.format(
                self.content if self.content else '',
                self.continuation_to.get_text())

        return self.content

    def get_real_bounding_box(self):
        page = self.page
        # Easier to read later on
        self_box = self.bounding_box
        # Margin of error for wonky pages
        weight = 1.2

        # Check if single article on page
        if not self.position_in_page or page.number_of_articles == 1:
            return [
                {'x': self_box['x0'], 'y': self_box['y0']},
                {'x': self_box['x0'], 'y': self_box['y1']},
                {'x': self_box['x1'], 'y': self_box['y1']},
                {'x': self_box['x1'], 'y': self_box['y0']},
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

                next_box = next_article.bounding_box

                if int(self_box['x1']) - int(self_box['x0']) > \
                   (int(next_box['x1']) - int(next_box['x0'])) * weight:
                    # Double column
                    return [
                        {'x': self_box['x0'], 'y': self_box['y0']},
                        {'x': self_box['x1'], 'y': self_box['y0']},
                        {'x': self_box['x1'], 'y': next_box['y0']},
                        {'x': next_box['x0'], 'y': next_box['y0']},
                        {'x': next_box['x0'], 'y': self_box['y1']},
                        {'x': self_box['x0'], 'y': self_box['y1']},
                    ]
                else:
                    # Single column
                    return [
                        {'x': self_box['x0'], 'y': self_box['y0']},
                        {'x': self_box['x0'], 'y': self_box['y1']},
                        {'x': self_box['x1'], 'y': self_box['y1']},
                        {'x': self_box['x1'], 'y': self_box['y0']}
                    ]
            elif self == last_article:
                # This is the last article on the page

                previous_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page - 1)
                prev_box = previous_article.bounding_box

                if int(self_box['x1']) - int(self_box['x0']) > \
                   (int(prev_box['x1']) - int(prev_box['x0'])) * weight:
                    # Double column
                    return [
                        {'x': self_box['x0'], 'y': prev_box['y1']},
                        {'x': prev_box['x1'], 'y': prev_box['y1']},
                        {'x': prev_box['x1'], 'y': self_box['y0']},
                        {'x': self_box['x1'], 'y': self_box['y0']},
                        {'x': self_box['x1'], 'y': self_box['y1']},
                        {'x': self_box['x0'], 'y': self_box['y1']},

                    ]
                else:
                    # Single column
                    return [
                        {'x': self_box['x0'], 'y': self_box['y0']},
                        {'x': self_box['x0'], 'y': self_box['y1']},
                        {'x': self_box['x1'], 'y': self_box['y1']},
                        {'x': self_box['x1'], 'y': self_box['y0']}
                    ]
            else:
                previous_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page - 1)
                next_article = page.articles_in_page.get(
                    position_in_page=self.position_in_page + 1)

                prev_box = previous_article.bounding_box
                next_box = next_article.bounding_box  # noqa

                # Check if over single or double column
                if int(self_box['x1']) - int(self_box['x0']) > \
                   (int(prev_box['x1']) - int(prev_box['x0'])) * weight \
                   and int(self_box['x1']) - int(self_box['x0']) > \
                   (int(next_box['x1']) - int(next_box['x0'])) * weight:
                    # Double column
                    return [
                        {'x': self_box['x0'], 'y': prev_box['y1']},
                        {'x': prev_box['x1'], 'y': prev_box['y1']},
                        {'x': prev_box['x1'], 'y': self_box['y0']},
                        {'x': self_box['x1'], 'y': self_box['y0']},
                        {'x': self_box['x1'], 'y': next_box['y0']},
                        {'x': next_box['x0'], 'y': next_box['y0']},
                        {'x': next_box['x0'], 'y': self_box['y1']},
                        {'x': self_box['x0'], 'y': self_box['y1']}
                    ]
                else:
                    # Single column
                    return [
                        {'x': self_box['x0'], 'y': self_box['y0']},
                        {'x': self_box['x0'], 'y': self_box['y1']},
                        {'x': self_box['x1'], 'y': self_box['y1']},
                        {'x': self_box['x1'], 'y': self_box['y0']}
                    ]
