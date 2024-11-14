from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Set the site domain'

    def handle(self, *args, **options):
        site_id = 1
        domain = '127.0.0.1'
        name = 'Transcendence'

        Site.objects.update_or_create(id=site_id, defaults={'domain': domain, 'name': name})
        self.stdout.write(self.style.SUCCESS('Successfully updated site domain'))