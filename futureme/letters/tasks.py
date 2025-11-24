from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from letters.models import Letter
from celery import current_app
from datetime import timedelta

@shared_task
def send_otp_email(email, otp_code):
    subject = 'Your OTP Code for FutureSelf'
    message = f'Your OTP code is: {otp_code}. It will expire in 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

@shared_task
def send_letter(letter_id):
    try:
        letter = Letter.objects.get(id=letter_id, is_delivered=False)
        send_mail(
            subject=f'A Letter From Your Past Self: {letter.title}',
            message=letter.content,
            from_email=settings.EMAIL_HOST_USER,
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
    except Letter.DoesNotExist:
        # Letter already sent or does not exist
        pass

@shared_task
def send_due_letters():
    now = timezone.now()
    due_letters = Letter.objects.filter(delivery_date__lte=now, is_delivered=False)
    for letter in due_letters:
        send_letter.delay(letter.id)

def schedule_letter_delivery(letter):
    eta = letter.delivery_date
    now = timezone.now()
    if eta.date() == now.date():
        # If delivery date is today, send 1 minute after now
        eta = now + timedelta(minutes=1)
    if eta > now:
        send_letter.apply_async(args=[letter.id], eta=eta)
    else:
        # If delivery date is in the past or now, send immediately
        send_letter.delay(letter.id)
