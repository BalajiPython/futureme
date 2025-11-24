from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from letters.models import Letter
import logging

logger = logging.getLogger(__name__)

def send_due_letters():
    now = timezone.now()
    due_letters = Letter.objects.filter(delivery_date__lte=now, is_delivered=False)
    logger.info(f"send_due_letters job started. Found {due_letters.count()} due letters.")
    for letter in due_letters:
        subject = f"Letter from your past self: {letter.title}"
        message = letter.content
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [letter.author.email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            letter.is_delivered = True
            letter.save()
            logger.info(f'Sent letter id {letter.id} to {letter.author.email}')
        except Exception as e:
            logger.error(f'Error sending letter id {letter.id}: {str(e)}')

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # Schedule job every minute
    scheduler.add_job(send_due_letters, 'interval', minutes=1, name='send_due_letters')
    register_events(scheduler)
    scheduler.start()
    logger.info("APScheduler started.")
