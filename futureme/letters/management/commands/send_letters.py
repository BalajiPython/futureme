from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from letters.models import Letter

class Command(BaseCommand):
    help = 'Send due letters to recipients'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        due_letters = Letter.objects.filter(
            delivery_date__lte=now,
            is_delivered=False
        )

        for letter in due_letters:
            try:
                send_mail(
                    subject=f'A Letter From Your Past Self: {letter.title}',
                    message=letter.content,
                    from_email=settings.EMAIL_HOST_USER,  # Use configured email
                    recipient_list=[letter.author.email],
                    fail_silently=False,
                    html_message=f"""
                    <html>
                        <body>
                            <h1>A Letter From Your Past Self</h1>
                            <h2>{letter.title}</h2>
                            <p>Written on: {letter.created_at.strftime('%Y-%m-%d')}</p>
                            <div>{letter.content}</div>
                            <hr>
                            <p>Sent from FutureSelf</p>
                        </body>
                    </html>
                    """
                )
                letter.is_delivered = True
                letter.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully sent letter {letter.id} to {letter.author.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send letter {letter.id}: {str(e)}')
                )
