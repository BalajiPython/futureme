from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
from letters.tasks import send_letter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send all overdue letters immediately'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f"\nCurrent time: {now}")
        
        # Get all overdue letters
        overdue_letters = Letter.objects.filter(
            delivery_date__lte=now,
            is_delivered=False
        ).order_by('delivery_date')
        
        self.stdout.write(f"\nFound {overdue_letters.count()} overdue letters")
        
        if overdue_letters.exists():
            self.stdout.write("\nProcessing overdue letters:")
            self.stdout.write("-" * 80)
            
            for letter in overdue_letters:
                self.stdout.write(f"\nLetter ID: {letter.id}")
                self.stdout.write(f"Title: {letter.title}")
                self.stdout.write(f"Author: {letter.author.email}")
                self.stdout.write(f"Delivery Date: {letter.delivery_date}")
                
                try:
                    send_letter(letter.id)
                    self.stdout.write(self.style.SUCCESS(f"Successfully sent letter {letter.id}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send letter {letter.id}: {str(e)}"))
                
                self.stdout.write("-" * 80)
        else:
            self.stdout.write(self.style.SUCCESS("No overdue letters found")) 