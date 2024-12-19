from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **options):
        name = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        passw = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        mail = os.environ.get("DJANGO_SUPERUSER_EMAIL")

        if not name or not passw or not mail:
            raise ValueError("The DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, and DJANGO_SUPERUSER_EMAIL environment variables must be set")

        if not User.objects.filter(username=name).exists():
            user = User.objects.create_superuser(name, mail, passw)
            user.save()
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))