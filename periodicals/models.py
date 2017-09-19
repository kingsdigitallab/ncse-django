from django.db import models


class Publication(models.Model):
    abbreviation = models.CharField(max_length=3, unique=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return '{}: {}'.format(self.abbreviation, self.title)


class Issue(models.Model):
    publication = models.ForeignKey(Publication)
    uid = models.CharField(max_length=32, unique=True)
    issue_date = models.DateField()
    number_of_pages = models.PositiveIntegerField(blank=True, null=True)
    pdf = models.FileField(upload_to='periodicals/')

    class Meta:
        ordering = ['publication', 'issue_date']

    def __str__(self):
        return '{}: {}'.format(self.publication, self.issue_date)


class Page(models.Model):
    issue = models.ForeignKey(Issue)
    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='periodicals/')

    class Meta:
        ordering = ['issue', 'number']

    def __str__(self):
        return '{}: {}'.format(self.issue, self.number)


class Article(models.Model):
    page = models.ForeignKey(Page)
    aid = models.CharField(max_length=32)
    title = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['page', 'aid']

    def __str__(self):
        return '{}: {}'.format(
            self.page, self.title if self.title else self.aid)
