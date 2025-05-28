from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
from letters.tasks import send_letter

class Command(BaseCommand):
    help = 'Process all old undelivered letters'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Get all undelivered letters
        undelivered_letters = Letter.objects.filter(is_delivered=False)
        
        self.stdout.write(f"Found {undelivered_letters.count()} undelivered letters")
        
        for letter in undelivered_letters:
            self.stdout.write(f"\nProcessing letter {letter.id}:")
            self.stdout.write(f"Title: {letter.title}")
            self.stdout.write(f"Author: {letter.author.email}")
            self.stdout.write(f"Created: {letter.created_at}")
            self.stdout.write(f"Delivery Date: {letter.delivery_date}")
            
            try:
                # Set delivery date to 1 minute ago to make it immediately due
                letter.delivery_date = now - timezone.timedelta(minutes=1)
                letter.save()
                
                # Try to send the letter
                self.stdout.write(f"Attempting to send letter to {letter.author.email}...")
                send_letter(letter.id)
                self.stdout.write(self.style.SUCCESS("Letter sent successfully"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to process letter: {str(e)}"))
                continue 