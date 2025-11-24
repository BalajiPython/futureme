from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test the email configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write("Testing email configuration...")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        try:
            send_mail(
                subject='Test Email from FutureSelf',
                message='This is a test email from FutureSelf. If you receive this, the email configuration is working correctly.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[test_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Test email sent successfully to {test_email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {str(e)}'))
            logger.error(f'Email test failed: {str(e)}', exc_info=True)
