from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.models import Letter
from datetime import timedelta
from letters.tasks import send_letter

class Command(BaseCommand):
    help = 'Make a letter due for immediate delivery'

    def add_arguments(self, parser):
        parser.add_argument('letter_id', type=int, help='ID of the letter to make due')

    def handle(self, *args, **options):
        letter_id = options['letter_id']
        
        try:
            letter = Letter.objects.get(id=letter_id)
            if letter.is_delivered:
                self.stdout.write(self.style.ERROR(f'Letter {letter_id} is already delivered'))
                return
                
            # Set delivery date to 1 minute ago to make it immediately due
            letter.delivery_date = timezone.now() - timedelta(minutes=1)
            letter.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully made letter {letter_id} due for immediate delivery'
            ))
            
            # Try to send the letter immediately
            try:
                self.stdout.write(f'Attempting to send letter {letter_id} to {letter.author.email}...')
                send_letter(letter.id)
                self.stdout.write(self.style.SUCCESS('Letter sent successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send letter: {str(e)}'))
                
        except Letter.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Letter {letter_id} does not exist')) 