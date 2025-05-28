from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check the status of a specific letter'

    def add_arguments(self, parser):
        parser.add_argument('letter_id', type=int, help='ID of the letter to check')

    def handle(self, *args, **options):
        letter_id = options['letter_id']
        now = timezone.now()
        
        try:
            letter = Letter.objects.get(id=letter_id)
            self.stdout.write(f"\nLetter Details:")
            self.stdout.write(f"ID: {letter.id}")
            self.stdout.write(f"Title: {letter.title}")
            self.stdout.write(f"Author: {letter.author.email}")
            self.stdout.write(f"Created: {letter.created_at}")
            self.stdout.write(f"Delivery Date: {letter.delivery_date}")
            self.stdout.write(f"Is Delivered: {letter.is_delivered}")
            self.stdout.write(f"Current Time: {now}")
            
            if not letter.is_delivered:
                if letter.delivery_date <= now:
                    self.stdout.write(self.style.WARNING("Letter is overdue and not delivered"))
                else:
                    self.stdout.write(self.style.SUCCESS("Letter is scheduled for future delivery"))
            else:
                self.stdout.write(self.style.SUCCESS("Letter has been delivered"))
                
        except Letter.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Letter {letter_id} does not exist")) 