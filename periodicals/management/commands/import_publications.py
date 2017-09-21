import os
import shutil
import subprocess
from zipfile import ZipFile

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from lxml import etree
from periodicals.models import Article, Issue, Page, Publication


class Command(BaseCommand):
    args = '<publication_path publication_path ...>'
    help = 'Imports/updates publications'

    def add_arguments(self, parser):
        parser.add_argument('publication_path', nargs='+', type=str)

    def handle(self, *args, **options):
        for publication_path in options['publication_path']:
            self._import_publication(publication_path)

    def _import_publication(self, publication_path):
        for root, dirs, files in os.walk(publication_path):
            for filename in files:
                if filename == 'TOC.xml':
                    tree = etree.parse(os.path.join(root, filename))
                    xmlroot = tree.getroot()

                    abbreviation = xmlroot.get('PUBLICATION')
                    self.stdout.write('Importing {}'.format(abbreviation))

                    publication, _ = Publication.objects.get_or_create(
                        abbreviation=abbreviation)
                    publication.description = xmlroot.get(
                        'PUBLICATION_DESCRIPTION')
                    publication.save()

                    self._import_issue(publication, xmlroot, root)

    def _import_issue(self, publication, xmlroot, dir):
        meta = xmlroot.xpath('Head_np/Meta')[0]
        link = xmlroot.xpath('Head_np/Link')[0]

        uid = meta.get('DOC_UID')

        self.stdout.write('- importing issue: {}'.format(uid))

        issue_date_parts = xmlroot.get('ISSUE_DATE').split('/')
        issue_date = parse_date('{}-{}-{}'.format(
            issue_date_parts[2], issue_date_parts[1], issue_date_parts[0]))
        number_of_pages = meta.get('PAGES_NUMBER')

        filename = link.get('SOURCE')
        pdf_path = os.path.join(dir, filename)
        pdf = File(open(pdf_path, 'rb'), name=filename)

        try:
            self._split_pdf(pdf_path, dir)
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(
                'Failed to split PDF: {}'.format(pdf_path)))
            self.stderr.write(self.style.ERROR(e.output))
            self.stderr.write(self.style.ERROR(
                'Failed to import issue: {}'.format(uid)))
            return

        try:
            issue = Issue.objects.get(uid=uid)
        except Issue.DoesNotExist:
            issue = Issue(uid=uid)

        issue.publication = publication
        issue.issue_date = issue_date
        issue.number_of_pages = number_of_pages
        issue.pdf = pdf

        issue.save()

        self._import_pages(issue, dir)

    def _split_pdf(self, pdf_path, output_path):
        process = subprocess.run(
            ['pdftk', pdf_path, 'burst', 'output', os.path.join(
                output_path, 'Pg%03d.pdf')],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.check_returncode()

    def _import_pages(self, issue, dir):
        extract_to = '_document'

        document = ZipFile(os.path.join(dir, 'Document.zip'), mode='r')
        document.extractall(path=extract_to)

        for root, dirs, files in os.walk(extract_to):
            for filename in files:
                if filename.endswith('.xml') and filename.startswith('Pg'):
                    self._import_page(issue, dir, root, filename)
            for filename in files:
                if filename.endswith('.xml') and filename.startswith('Ar'):
                    self._import_article(issue, root, filename)

        shutil.rmtree(extract_to)

    def _import_page(self, issue, pdfdir, dir, filename):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()
        meta = xmlroot.xpath('Meta')[0]

        number = meta.get('PAGE_NO')
        try:
            page = Page.objects.get(issue=issue, number=number)
        except Page.DoesNotExist:
            page = Page(issue=issue)

        page.number = number

        basename = os.path.splitext(filename)[0]

        image_filename = basename + '.png'
        image = File(
            open(os.path.join(dir, 'Img', image_filename), 'rb'),
            name='{}/{}'.format(meta.get('RELEASE_NO'), image_filename))
        page.image = image

        pdf_filename = basename + '.pdf'
        pdf = File(
            open(os.path.join(pdfdir, pdf_filename), 'rb'),
            name='{}/{}'.format(meta.get('RELEASE_NO'), pdf_filename))
        page.pdf = pdf

        page.save()

    def _import_article(self, issue, dir, filename):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()

        aid = xmlroot.get('ID')

        try:
            page_number = xmlroot.get('PAGE_NO')
            page = Page.objects.get(issue=issue, number=page_number)
        except Page.DoesNotExist:
            self.stderr.write(self.style.WARNING(
                'Page not found for issue {} article {}'.format(issue, aid)))
            return

        try:
            article = Article.objects.get(page=page, aid=aid)
        except Article.DoesNotExist:
            article = Article(page=page)

        meta = xmlroot.xpath('Meta')[0]
        content = xmlroot.xpath('Content')[0]
        content_xpath = ('//text()[normalize-space() and '
                         'parent::node()[name() != "Q" and name () != "q"]]')

        article.aid = aid
        article.title = meta.get('NAME')
        article.description = meta.get('DESCRIPTION')
        article.content = ' '.join(content.xpath(content_xpath))

        article.save()
