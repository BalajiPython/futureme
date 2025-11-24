from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check timing details of all letters'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f"\nCurrent time: {now}")
        self.stdout.write(f"Timezone: {timezone.get_current_timezone()}")
        
        # Get all letters
        letters = Letter.objects.all().order_by('delivery_date')
        
        self.stdout.write(f"\nTotal letters: {letters.count()}")
        
        if letters.exists():
            self.stdout.write("\nAll Letters:")
            self.stdout.write("-" * 80)
            
            for letter in letters:
                time_until_due = letter.delivery_date - now
                is_due = letter.delivery_date <= now
                
                self.stdout.write(f"\nLetter ID: {letter.id}")
                self.stdout.write(f"Title: {letter.title}")
                self.stdout.write(f"Author: {letter.author.email}")
                self.stdout.write(f"Created: {letter.created_at}")
                self.stdout.write(f"Delivery Date: {letter.delivery_date}")
                self.stdout.write(f"Is Delivered: {letter.is_delivered}")
                self.stdout.write(f"Time until due: {time_until_due}")
                self.stdout.write(f"Is due now: {is_due}")
                
                if not letter.is_delivered:
                    if is_due:
                        self.stdout.write(self.style.WARNING("Status: OVERDUE - Should be delivered now"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Status: Scheduled for delivery in {time_until_due}"))
                else:
                    self.stdout.write(self.style.SUCCESS("Status: DELIVERED"))
                
                self.stdout.write("-" * 80)
        else:
            self.stdout.write(self.style.SUCCESS("No letters found")) 