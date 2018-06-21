import logging
import os
import re
import shutil
from django.core.management.base import BaseCommand
from lxml import etree
from periodicals.models import (Issue, Publication)


class Command(BaseCommand):
    args = '<publication_path publication_path ...>'
    logger = logging.getLogger(__name__)
    extract_to = '_document'

    # Types to import
    import_ar = False
    import_ad = False
    import_pc = False

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

                    data = xmlroot.xpath('Head_np/Application_Data')
                    if not data:
                        self.logger.critical(
                            '** Skipping publication {}/{} because metadata is\
                            missing'.format(publication_path, root))
                        continue

                    data = data[0]
                    abbreviation = None
                    title = None

                    abbreviation = xmlroot.get('PUBLICATION')
                    publication_list = Publication.objects.filter(
                        abbreviation=abbreviation)

                    if publication_list.exists():
                        publication = publication_list[0]

                        self.logger.info('Importing {}: {}'.format(
                            abbreviation, title))

                        publication.description = xmlroot.get(
                            'PUBLICATION_DESCRIPTION')
                        publication.save()

                        self._import_issue(publication, xmlroot, root)

    def _generate_abbreviation_from_title(self, title):
        return re.sub('[^A-Z]', '', title)

    def _import_issue(self, publication, xmlroot, dir):
        meta = xmlroot.xpath('Head_np/Meta')[0]
        uid = meta.get('DOC_UID')

        # This fixes an issue where olive sometimes doesn't
        # include a UID field:
        if not uid:
            base_href = meta.get('BASE_HREF').split('/')
            uid = "{}_{}".format(base_href[0], '/'.join(base_href[1:4][::-1]))

        self.logger.info('- importing issue: {}'.format(uid))

        if '_' not in dir:
            issue_list = Issue.objects.filter(uid=uid)
            if issue_list.exists():
                issue = issue_list[0]
                data = xmlroot.xpath('Body_np/Section/Page')

                for p in data:
                    no = p.get('PAGE_NO')
                    label = p.get('PAGE_LABEL')
                    page_list = issue.pages.filter(number=no)

                    if page_list.exists():
                        page = page_list[0]
                        page.label = label
                        page.save()

        else:
            self.logger.critical('** Skipping issue {} because the\
                directory {} failed to meet requirements'.format(
                uid, dir))
