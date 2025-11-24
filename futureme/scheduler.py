from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from letters.models import Letter
import logging

logger = logging.getLogger(__name__)

def send_due_letters():
    try:
        now = timezone.now()
        due_letters = Letter.objects.filter(delivery_date__lte=now, is_delivered=False)
        logger.info(f"send_due_letters job started. Found {due_letters.count()} due letters.")
        
        for letter in due_letters:
            subject = f"Letter from your past self: {letter.title}"
            message = letter.content
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [letter.author.email]
            
            logger.info(f"Attempting to send letter {letter.id} to {letter.author.email}")
            logger.info(f"Email settings - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}")
            logger.info(f"From email: {from_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Message length: {len(message)} characters")
            
            try:
                logger.info("Calling send_mail function...")
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                logger.info(f'Successfully sent letter id {letter.id} to {letter.author.email}')
                letter.is_delivered = True
                letter.save()
                logger.info(f'Marked letter {letter.id} as delivered')
            except Exception as e:
                logger.error(f'Error sending letter id {letter.id}: {str(e)}')
                logger.error(f'Email configuration:')
                logger.error(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
                logger.error(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
                logger.error(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
                logger.error(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
                logger.error(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
                logger.error(f'  Recipient: {recipient_list}')
                logger.error(f'  Subject: {subject}')
                logger.error(f'  Message length: {len(message)}')
    except Exception as e:
        logger.error(f'Error in send_due_letters: {str(e)}')

scheduler = None

def start_scheduler():
    global scheduler
    if scheduler is not None:
        logger.info("Scheduler already running")
        return
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(
        send_due_letters,
        'interval',
        minutes=1,
        id='send_due_letters',
        max_instances=1,
        replace_existing=True,
    )
    register_events(scheduler)
    try:
        scheduler.start()
        logger.info("APScheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")

def stop_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")

def get_scheduled_jobs():
    global scheduler
    if scheduler is not None:
        return scheduler.get_jobs()
    return []

def restart_scheduler():
    stop_scheduler()
    start_scheduler()

def check_scheduler_status():
    if scheduler is not None:
        logger.info("Scheduler is running")
    else:
        logger.info("Scheduler is not running")

def send_test_email():
    try:
        send_mail(
            subject="Test Email",
            message="This is a test email",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["test@example.com"],
            fail_silently=False,
        )
        logger.info("Test email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
