from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from letters.models import Letter
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create a test letter for delivery in 2 minutes'

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

            # Calculate delivery time (2 minutes from now)
            now = timezone.now()
            delivery_time = now + timedelta(minutes=2)
            
            self.stdout.write(f"\nCurrent time (UTC): {now}")
            self.stdout.write(f"Delivery time (UTC): {delivery_time}")
            
            # Create test letter
            letter = Letter.objects.create(
                author=user,
                title=f'Test Letter - 2 Min Delivery',
                content=f'This is a test letter created at {now.strftime("%Y-%m-%d %H:%M:%S")} UTC\n'
                       f'It should be delivered at {delivery_time.strftime("%Y-%m-%d %H:%M:%S")} UTC',
                delivery_date=delivery_time
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'\nCreated test letter:')
            )
            self.stdout.write(f"Letter ID: {letter.id}")
            self.stdout.write(f"Title: {letter.title}")
            self.stdout.write(f"Author: {user.email}")
            self.stdout.write(f"Delivery Date: {letter.delivery_date}")
            self.stdout.write(f"Is Delivered: {letter.is_delivered}")
            
            # Show time until delivery
            time_until_delivery = delivery_time - now
            self.stdout.write(f"\nTime until delivery: {time_until_delivery}")
            
            self.stdout.write(
                self.style.SUCCESS('\nTest letter created successfully!')
            )
            self.stdout.write(
                self.style.WARNING('\nWatch the Django console for delivery status...')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            ) 