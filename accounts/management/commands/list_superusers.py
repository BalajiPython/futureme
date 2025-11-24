from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Lists all superusers in the system'

    def handle(self, *args, **options):
        superusers = User.objects.filter(is_superuser=True)
        
        if superusers.exists():
            self.stdout.write(self.style.SUCCESS(f'Found {superusers.count()} superuser(s):'))
            for user in superusers:
                self.stdout.write(f'- Email: {user.email}')
                self.stdout.write(f'  Last Login: {user.last_login}')
                self.stdout.write(f'  Date Joined: {user.date_joined}')
                self.stdout.write('---')
        else:
            self.stdout.write(self.style.WARNING('No superusers found in the system.')) 