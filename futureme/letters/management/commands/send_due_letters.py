from django.core.management.base import BaseCommand
from letters.models import Letter
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send due letters to users'

    def handle(self, *args, **options):
        now = timezone.now()
        due_letters = Letter.objects.filter(delivery_date__lte=now, is_delivered=False)
        for letter in due_letters:
            subject = f"Letter from your past self: {letter.title}"
            message = letter.content
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [letter.author.email]
            try:
                send_mail(subject, message, from_email, recipient_list)
                letter.is_delivered = True
                letter.save()
                self.stdout.write(self.style.SUCCESS(f'Sent letter id {letter.id} to {letter.author.email}'))
            except Exception as e:
                logger.error(f'Error sending letter id {letter.id}: {str(e)}')
                self.stdout.write(self.style.ERROR(f'Failed to send letter id {letter.id}'))
