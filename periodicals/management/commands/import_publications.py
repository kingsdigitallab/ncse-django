import os
import json
import logging
import shutil
from zipfile import ZipFile
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from lxml import etree
from periodicals.models import Article, ArticleType, Issue, Page, Publication


class Command(BaseCommand):
    args = '<publication_path publication_path ...>'
    help = 'Imports/updates publications'
    logger = logging.getLogger(__name__)
    extract_to = '_document'

    def add_arguments(self, parser):
        parser.add_argument('publication_path', nargs='+', type=str)

    def handle(self, *args, **options):
        for publication_path in options['publication_path']:
            self._import_publication(publication_path)

        # Cleanup
        if os.path.isdir(self.extract_to):
            shutil.rmtree(self.extract_to)

        # Re-save to generate the ordering
        publications = Publication.objects.all()
        for p in publications:
            p.save()

    # Helper object:
    def _str_to_box(self, input):
        coords = input.split(' ')
        if len(coords) == 4:
            # Success
            return {'x0': coords[0], 'x1': coords[2],
                    'y0': coords[1], 'y1': coords[3]}
        else:
            return {}

    def _import_publication(self, publication_path):
        for root, dirs, files in os.walk(publication_path):
            for filename in files:
                if filename == 'TOC.xml':
                    tree = etree.parse(os.path.join(root, filename))
                    xmlroot = tree.getroot()

                    abbreviation = xmlroot.get('PUBLICATION')
                    self.logger.info('Importing {}'.format(abbreviation))

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

        # This fixes an issue where olive sometimes doesn't
        # include a UID field:
        if not uid:
            base_href = meta.get('BASE_HREF').split('/')
            uid = "{}_{}".format(base_href[0], '/'.join(base_href[1:4][::-1]))

        self.logger.info('- importing issue: {}'.format(uid))

        issue_date_parts = xmlroot.get('ISSUE_DATE').split('/')
        issue_date = parse_date('{}-{}-{}'.format(
            issue_date_parts[2], issue_date_parts[1], issue_date_parts[0]))
        number_of_pages = meta.get('PAGES_NUMBER')

        if '_' not in dir:
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
        else:
            self.logger.critical('** Skipping issue {} because the\
                directory {} failed to meet requirements'.format(
                uid, dir))

    def _import_pages(self, issue, dir):
        self.logger.debug('- unzipping Document.zip')
        document = ZipFile(os.path.join(dir, 'Document.zip'), mode='r')

        if os.path.isdir(self.extract_to):
            shutil.rmtree(self.extract_to)

        try:
            document.extractall(path=self.extract_to)
        except NotADirectoryError:
            # This is to fix broken zip exports in Olive
            file_list = [f for f in document.namelist() if '.' in f]
            if os.path.isdir(self.extract_to):
                shutil.rmtree(self.extract_to)
            document.extractall(path=self.extract_to, members=file_list)

        for root, dirs, files in os.walk(self.extract_to):
            for filename in files:
                if filename.endswith('.xml') and filename.startswith('Pg'):
                    self._import_page(issue, dir, root, filename)
            for filename in files:
                if filename.endswith('.xml') and not filename.startswith('P'):
                    self._import_article(issue, root, filename)

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
        self.logger.debug('- - importing article: {}'.format(aid))

        try:
            page_number = xmlroot.get('PAGE_NO')
            page = Page.objects.get(issue=issue, number=page_number)
        except Page.DoesNotExist:
            self.logger.error(
                '-- page not found for issue {} article {}'.format(
                    issue, aid))
            return
        except Exception as e:
            self.logger.error('-- failed to get page_number/page')
            self.logger.error(e.get_message())
            return

        try:
            article = Article.objects.get(issue=issue, aid=aid)
        except Article.DoesNotExist:
            article = Article(issue=issue, page=page, aid=aid)

        meta = xmlroot.xpath('Meta')[0]

        article.page = page
        article.position_in_page = xmlroot.get('INDEX_IN_DOC')
        article.title = meta.get('NAME')
        article.description = meta.get('DESCRIPTION')

        header_text = ''
        header = xmlroot.xpath('HedLine_hl1')
        if header:
            header_xpath = (
                'Primitive/node()/text()[normalize-space() and '
                'parent::node()[name() != "Q" and name () != "q"]]')
            header_text = ' '.join(header[0].xpath(header_xpath))

        content_text = ''
        content = xmlroot.xpath('Content')
        if content:
            content_xpath = (
                '//text()[normalize-space() and '
                'parent::node()[name() != "Q" and name () != "q"]]')
            content_text = '{}{}'.format(
                article.content, ' '.join(content[0].xpath(content_xpath)))

        article.content = '{}{}'.format(header_text, content_text)

        article.bounding_box = self._str_to_box(xmlroot.get('BOX'))
        article.save()

        self._add_article_continuation(issue, dir, filename, article)
        self._add_article_entity_type(issue, dir, filename, article)
        self._add_article_html(issue, dir, filename, article)
        self._add_article_snippet_image(issue, dir, filename, article)
        self._add_article_words_to_page(issue, dir, filename, page, article)

    def _add_article_continuation(self, issue, dir, filename, article):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()
        aid = xmlroot.get('ID')

        if xmlroot.get('CONTINUATION_FROM'):
            continuation_from = xmlroot.get('CONTINUATION_FROM')
            self.logger.debug(
                '-- article {} continuation from {}'.format(
                    aid, continuation_from))

            continuation_from_article, _ = Article.objects.get_or_create(
                issue=issue, aid=continuation_from)
            continuation_from_article.continuation_to = article
            continuation_from_article.save()

            article.continuation_from = continuation_from_article
            article.save()

    def _add_article_entity_type(self, issue, dir, filename, article):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()

        if xmlroot.get('ENTITY_TYPE'):
            article.article_type, _ = ArticleType.objects.get_or_create(
                title=xmlroot.get('ENTITY_TYPE'))

            article.save()

    def _add_article_html(self, issue, dir, filename, article):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()

        # Pretty HTML
        header_html = ''
        header = xmlroot.xpath('HedLine_hl1')
        if len(header):
            header_html = '<p class="article-header">{}</p>\n'.format(
                ' '.join(header[0].xpath(
                    'Primitive/node()/text()[normalize-space() and '
                    'parent::node()[name() != "Q" and name () != "q"]]')))

        content_html = ''
        content = xmlroot.xpath('Content')
        if content:
            for primitive in content[0].xpath('Primitive'):
                content_html = '{}<p class="article-content">{}</p>\n'.format(
                    content_html, ' '.join(primitive.xpath(
                        'node()/text()[normalize-space() and '
                        'parent::node()[name() != "Q" and name () != "q"]]')))

        article.content_html = '{}{}'.format(header_html, content_html)

        article.save()

    def _add_article_snippet_image(self, issue, dir, filename, article):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()
        meta = xmlroot.xpath('Meta')[0]

        # Get the snippet image
        image_filename = xmlroot.get('SNP')
        # Sanity check
        if image_filename:
            image = File(
                open(os.path.join(dir, 'Img', image_filename), 'rb'),
                name='{}/{}'.format(meta.get('RELEASE_NO'), image_filename))

            article.title_image = image
            article.save()

    def _add_article_words_to_page(self, issue, dir, filename, page, article):
        tree = etree.parse(os.path.join(dir, filename))
        xmlroot = tree.getroot()

        # Get page words
        words = page.words

        # Check if we have a dict, if not, create it
        if not isinstance(words, dict):
            words = json.loads(words)

        # Get our xpaths
        words_xpath = xmlroot.xpath('node()/Primitive/W')
        joined_words_xpath = xmlroot.xpath('node()/Primitive/QW')

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
