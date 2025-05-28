from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
from letters.tasks import send_letter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send all scheduled messages immediately'

    def handle(self, *args, **options):
        # Get all undelivered letters
        undelivered_letters = Letter.objects.filter(is_delivered=False).order_by('delivery_date')
        
        self.stdout.write(f"Found {undelivered_letters.count()} scheduled letters")
        
        for letter in undelivered_letters:
            self.stdout.write(f"\nProcessing letter {letter.id}:")
            self.stdout.write(f"Title: {letter.title}")
            self.stdout.write(f"Author: {letter.author.email}")
            self.stdout.write(f"Created: {letter.created_at}")
            self.stdout.write(f"Original Delivery Date: {letter.delivery_date}")
            
            try:
                # Try to send the letter
                self.stdout.write(f"Attempting to send letter to {letter.author.email}...")
                send_letter(letter.id)
                self.stdout.write(self.style.SUCCESS("Letter sent successfully"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to send letter: {str(e)}"))
                continue 