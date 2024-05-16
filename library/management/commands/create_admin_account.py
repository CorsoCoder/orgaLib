from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = "create admin account"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        parser.add_argument('--email', type=str)
        parser.add_argument('--password', type=str)

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            User.objects.create_superuser(username, email, password)
        except IntegrityError:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

        self.stdout.write(self.style.SUCCESS("admin account succesfully created"))
