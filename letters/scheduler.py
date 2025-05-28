from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from letters.tasks import send_letter
from letters.models import Letter
from django.utils import timezone
from django.db import transaction
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

def check_and_send_letters():
    """Check for due letters and send them immediately"""
    try:
        now = timezone.now()  # This is already in UTC
        logger.info(f"\n=== Checking for due letters at {now} (UTC) ===")
        
        # First get eligible letters without locking
        due_letters = Letter.objects.filter(
            delivery_date__lte=now + timedelta(minutes=5),
            delivery_date__gte=now - timedelta(minutes=5),
            is_delivered=False,
            delivery_attempts__lt=3
        ).exclude(
            last_delivery_attempt__gte=now - timedelta(minutes=5)
        ).order_by('delivery_date')[:10]  # Process only 10 letters at a time
        
        if not due_letters:
            logger.info("No due letters found")
            return
            
        logger.info(f"Found {due_letters.count()} due letters")
        
        # Process each due letter
        for letter in due_letters:
            try:
                logger.info(f"\nProcessing letter {letter.id}:")
                logger.info(f"Title: {letter.title}")
                logger.info(f"Delivery date (UTC): {letter.delivery_date}")
                logger.info(f"Current time (UTC): {now}")
                logger.info(f"Time difference: {now - letter.delivery_date}")
                logger.info(f"Delivery attempts: {letter.delivery_attempts}")
                logger.info(f"Last attempt: {letter.last_delivery_attempt}")
                logger.info(f"Recipient: {letter.author.email}")
                
                # Send the letter
                send_letter(letter.id)
                logger.info(f"Successfully sent letter {letter.id}")
                
            except Exception as e:
                logger.error(f"Failed to send letter {letter.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in check_and_send_letters: {str(e)}")

def start_scheduler():
    try:
        # Create scheduler with a single thread to prevent concurrent database access
        scheduler = BackgroundScheduler(
            job_defaults={
                'coalesce': True,  # Only run once if multiple executions are missed
                'max_instances': 1  # Only allow one instance of the job to run at a time
            }
        )
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # Add the job to check and send letters every 30 seconds
        scheduler.add_job(
            check_and_send_letters,
            trigger=IntervalTrigger(seconds=30),
            id='check_and_send_letters',
            replace_existing=True,
            max_instances=1
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Letter scheduler started successfully")
        
        # Check for due letters immediately
        check_and_send_letters()
        
    except Exception as e:
        logger.error(f"Failed to start letter scheduler: {str(e)}")
        # Don't raise the exception - we want the app to start even if scheduler fails 