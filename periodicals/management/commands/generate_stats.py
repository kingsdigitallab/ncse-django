from django.core.management.base import BaseCommand
from periodicals.models import Page
import time


class Command(BaseCommand):
    help = 'Re-generates statistics.'

    def handle(self, *args, **options):
        print()
        print('##############################################')
        print('# Generating stats, this may take a while... #')
        print('##############################################')
        print()

        obj_count = Page.objects.count()
        current_count = 1
        for p in Page.objects.all():
            pct = int((current_count / obj_count) * 100)
            self._out('  Re-saving objects... {}%'.format(pct))
            current_count += 1
            p.save()

    def _out(self, message):
        self.stdout.write(message, ending='\r')
        self.stdout.flush()
        time.sleep(0.01)