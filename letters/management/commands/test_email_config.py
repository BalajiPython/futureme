from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from letters.models import Letter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test email configuration and send a test email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test to')
        parser.add_argument('--letter_id', type=int, help='Use email from this letter')

    def handle(self, *args, **options):
        self.stdout.write("Testing email configuration...")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Get recipient email
        recipient_email = options.get('email')
        if not recipient_email and options.get('letter_id'):
            try:
                letter = Letter.objects.get(id=options['letter_id'])
                recipient_email = letter.author.email
                self.stdout.write(f"Using email from letter {options['letter_id']}: {recipient_email}")
            except Letter.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Letter {options['letter_id']} not found"))
                return
        
        if not recipient_email:
            self.stdout.write(self.style.ERROR("Please provide either --email or --letter_id"))
            return
        
        try:
            # Send test email
            send_mail(
                subject='Test Email from FutureMe',
                message='This is a test email to verify your email configuration.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Test email sent successfully!'))
            self.stdout.write(f"Email was sent to: {recipient_email}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))
            logger.error(f"Email error details: {str(e)}") 