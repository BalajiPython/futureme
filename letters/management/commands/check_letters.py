from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check all letters with detailed information'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Get all letters
        all_letters = Letter.objects.all().order_by('delivery_date')
        
        self.stdout.write(f"\nCurrent time: {now}")
        self.stdout.write(f"Total letters: {all_letters.count()}\n")
        
        if all_letters.exists():
            self.stdout.write("All Letters:")
            self.stdout.write("-" * 80)
            
            for letter in all_letters:
                self.stdout.write(f"\nLetter ID: {letter.id}")
                self.stdout.write(f"Title: {letter.title}")
                self.stdout.write(f"Author: {letter.author.email}")
                self.stdout.write(f"Created: {letter.created_at}")
                self.stdout.write(f"Delivery Date: {letter.delivery_date}")
                self.stdout.write(f"Is Delivered: {letter.is_delivered}")
                
                if not letter.is_delivered:
                    if letter.delivery_date <= now:
                        self.stdout.write(self.style.WARNING("Status: OVERDUE - Should be delivered now"))
                    else:
                        time_until_delivery = letter.delivery_date - now
                        self.stdout.write(self.style.SUCCESS(f"Status: Scheduled for delivery in {time_until_delivery}"))
                else:
                    self.stdout.write(self.style.SUCCESS("Status: DELIVERED"))
                
                self.stdout.write("-" * 80)
        else:
            self.stdout.write(self.style.SUCCESS("No letters found")) 