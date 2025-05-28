from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Show detailed information about all letters'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f"\nCurrent server time: {now}")
        self.stdout.write(f"Timezone: {timezone.get_current_timezone()}")
        
        # Get ALL letters
        letters = Letter.objects.all().order_by('delivery_date')
        
        self.stdout.write(f"\nTotal letters in database: {letters.count()}")
        
        if letters.exists():
            self.stdout.write("\nDetailed Letter Information:")
            self.stdout.write("=" * 80)
            
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
                
                # Show raw database values
                self.stdout.write("\nRaw Database Values:")
                self.stdout.write(f"delivery_date (raw): {letter.delivery_date}")
                self.stdout.write(f"created_at (raw): {letter.created_at}")
                self.stdout.write(f"is_delivered (raw): {letter.is_delivered}")
                
                if not letter.is_delivered:
                    if is_due:
                        self.stdout.write(self.style.WARNING("Status: OVERDUE - Should be delivered now"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Status: Scheduled for delivery in {time_until_due}"))
                else:
                    self.stdout.write(self.style.SUCCESS("Status: DELIVERED"))
                
                self.stdout.write("=" * 80)
        else:
            self.stdout.write(self.style.WARNING("No letters found in database")) 