from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def handle(self, *args, **kwargs):
        try:
            send_mail(
                subject='Test Email from FutureSelf',
                message='This is a test email to verify your email configuration.',
                from_email=settings.EMAIL_HOST_USER,  # Uses email from .env
                recipient_list=[settings.EMAIL_HOST_USER],  # Sends to same email
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Test email sent successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))
