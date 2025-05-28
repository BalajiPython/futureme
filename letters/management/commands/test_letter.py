from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from letters.models import Letter

class Command(BaseCommand):
    help = 'Create a test letter for immediate delivery'

    def handle(self, *args, **kwargs):
        try:
            # Get admin user
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(
                    self.style.WARNING('Creating admin user...')
                )
                user = User.objects.create_superuser(
                    username='admin@futureme.com',
                    email='admin@futureme.com',
                    password='admin123'
                )

            # Create test letter
            letter = Letter.objects.create(
                author=user,
                title=f'Test Letter {timezone.now().strftime("%H:%M:%S")}',
                content='This is a new test letter sent at ' + timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                delivery_date=timezone.now()
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created test letter for {user.email}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
