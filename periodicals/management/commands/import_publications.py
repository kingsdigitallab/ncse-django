import os
import json
import shutil
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

    # Helper object:
    def _str_to_box(self, input):
        coords = input.split(' ')
        if len(coords) == 4:
            # Success
            return {"x0": coords[0],
                    "x1": coords[2],
                    "y0": coords[1],
                    "y1": coords[3]
                    }
        else:
            return {}

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
            issue = Issue.objects.get(uid=uid)
        except Issue.DoesNotExist:
            issue = Issue(uid=uid)

        issue.publication = publication
        issue.issue_date = issue_date
        issue.number_of_pages = number_of_pages
        issue.pdf = pdf

        issue.save()

        self._import_pages(issue, dir)

    def _import_pages(self, issue, dir):
        extract_to = '_document'
        self.stdout.write('- unzipping Document.zip')
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

        height = meta.get('PAGE_HEIGHT')
        number = meta.get('PAGE_NO')
        width = meta.get('PAGE_WIDTH')

        try:
            page = Page.objects.get(issue=issue, number=number)
        except Page.DoesNotExist:
            page = Page(issue=issue)

        page.height = height
        page.number = number
        page.width = width

        basename = os.path.splitext(filename)[0]

        image_filename = basename + '.png'
        image = File(
            open(os.path.join(dir, 'Img', image_filename), 'rb'),
            name='{}/{}'.format(meta.get('RELEASE_NO'), image_filename))
        page.image = image
        page.save()

    def _import_article(self, issue, dir, filename):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()

        aid = xmlroot.get('ID')
        self.stdout.write('- - importing article: {}'.format(aid))

        try:
            page_number = xmlroot.get('PAGE_NO')
            page = Page.objects.get(issue=issue, number=page_number)
        except Page.DoesNotExist:
            self.stderr.write(self.style.NOTICE(
                '-- page not found for issue {} article {}'.format(
                    issue, aid)))
            return

        try:
            article = Article.objects.get(issue=issue, aid=aid)
        except Article.DoesNotExist:
            article = Article(issue=issue, page=page, aid=aid)

        meta = xmlroot.xpath('Meta')[0]
        content = xmlroot.xpath('Content')[0]
        content_xpath = ('//text()[normalize-space() and '
                         'parent::node()[name() != "Q" and name () != "q"]]')

        article.page = page
        article.position_in_page = xmlroot.get('INDEX_IN_DOC')
        article.title = meta.get('NAME')
        article.description = meta.get('DESCRIPTION')
        article.content = ' '.join(content.xpath(content_xpath))
        article.bounding_box = self._str_to_box(xmlroot.get('BOX'))

        article.save()

        if xmlroot.get('CONTINUATION_FROM'):
            continuation_from = xmlroot.get('CONTINUATION_FROM')
            self.stdout.write(self.style.WARNING(
                '-- article {} continuation from {}'.format(
                    aid, continuation_from)))

            continuation_from_article, _ = Article.objects.get_or_create(
                issue=issue, aid=continuation_from)
            continuation_from_article.continuation_to = article
            continuation_from_article.save()

            article.continuation_from = continuation_from_article
            article.save()

        # Here we are going to grab the words from the page
        # and merge them with the ones from this article.

        # This is a json object, we store the words and their coordinates
        # in the following format:
        # { '<word>': [{'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}]}

        # Get page words
        words = page.words

        # Check if we have a dict, if not, create it
        if not isinstance(words, dict):
            words = json.loads(words)

        # Get our xpaths
        words_xpath = xmlroot.xpath('node()/Primitive/W')
        joined_words_xpath = xmlroot.xpath('node()/Primitive/QW')

        self.stdout.write('- - - importing words')

        # Iterate over words, adding them to the list
        for word in words_xpath:
            # word.text, word.get('box')
            text = word.text.lower()
            if text not in words:
                words[text] = []
            words[text].append(self._str_to_box(word.get('BOX')))

        # Iterate over our joined words (fixes)
        for word in joined_words_xpath:
            text = word.text.lower()
            if text not in words:
                words[text] = []

            # Get the QID
            qid = word.get('QID')

            # Get nodes that form parts of our joint words
            # There are <q> and <Q>
            qid_xpath = xmlroot.xpath(
                'node()/Primitive/q[@QID=\'{}\']'.format(qid))
            qid_xpath_cap = xmlroot.xpath(
                'node()/Primitive/Q[@QID=\'{}\']'.format(qid))

            for part in qid_xpath:
                words[text].append(self._str_to_box(part.get('BOX')))

            for part in qid_xpath_cap:
                words[text].append(self._str_to_box(part.get('BOX')))

        # Save them back to the page
        page.words = words
        page.save()
