from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from letters.models import Letter
from datetime import timedelta
import logging
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend

logger = logging.getLogger(__name__)

def send_otp_email(email, otp_code):
    subject = 'Your OTP Code for FutureSelf'
    message = f'Your OTP code is: {otp_code}. It will expire in 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def send_letter(letter_id):
    """Send a letter to its author"""
    try:
        # First check if letter exists and is eligible for sending without locking
        letter = Letter.objects.filter(
            id=letter_id,
            is_delivered=False,
            delivery_attempts__lt=3
        ).first()
        
        if not letter:
            logger.info(f"Letter {letter_id} not found or not eligible for sending")
            return
            
        # Check if we've tried to deliver this letter recently
        if letter.last_delivery_attempt and (timezone.now() - letter.last_delivery_attempt) < timedelta(minutes=5):
            logger.info(f"Letter {letter_id} was attempted recently at {letter.last_delivery_attempt}, skipping")
            return
        
        # Double check if the letter is due
        now = timezone.now()
        if letter.delivery_date > now + timedelta(minutes=5):
            logger.info(f"Letter {letter_id} not due yet (due at {letter.delivery_date}, current time {now}), skipping")
            return
        
        # Use a small transaction only for the critical update
        with transaction.atomic():
            # Try to acquire the letter with a lock only for the update
            letter = Letter.objects.select_for_update(nowait=True).filter(
                id=letter_id,
                is_delivered=False,
                delivery_attempts__lt=3
            ).first()
            
            if not letter:
                logger.info(f"Letter {letter_id} was processed by another worker")
                return
            
            # Increment delivery attempts
            letter.increment_delivery_attempt()
            
            logger.info(f"Sending letter {letter_id} to {letter.author.email}")
            logger.info(f"Delivery date: {letter.delivery_date}")
            logger.info(f"Current time: {now}")
            logger.info(f"Time difference: {now - letter.delivery_date}")
            logger.info(f"Delivery attempt: {letter.delivery_attempts}")
            
            # Send the email
            send_mail(
                subject=f'Your Future Letter: {letter.title}',
                message=letter.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[letter.author.email],
                fail_silently=False,
            )
            
            # Mark as delivered
            letter.mark_as_sent()
            logger.info(f"Successfully sent letter {letter_id} to {letter.author.email}")
            
    except Letter.DoesNotExist:
        logger.error(f"Letter {letter_id} not found")
    except Exception as e:
        logger.error(f"Failed to send letter {letter_id}: {str(e)}")
        raise

def process_due_letters():
    """Process all due letters that haven't been delivered yet"""
    now = timezone.now()
    logger.info(f"Checking for due letters at {now}")
    
    try:
        # Get due letters
        due_letters = Letter.objects.filter(
            delivery_date__lte=now,
            is_delivered=False
        ).order_by('delivery_date')
        
        logger.info(f"Found {due_letters.count()} due letters to process")
        
        for letter in due_letters:
            logger.info(f"Processing letter {letter.id}: {letter.title}")
            logger.info(f"Delivery date: {letter.delivery_date}")
            logger.info(f"Recipient: {letter.author.email}")
            
            try:
                send_letter(letter.id)
                logger.info(f"Successfully processed letter {letter.id}")
            except Exception as e:
                logger.error(f"Error processing letter {letter.id}: {str(e)}")
                # Don't raise the exception - continue with next letter
                continue
                
    except Exception as e:
        logger.error(f"Error in process_due_letters: {str(e)}")
        # Don't raise the exception - let the scheduler retry

def schedule_letter_delivery(letter):
    """Schedule a letter for delivery"""
    try:
        now = timezone.now()
        # If delivery date is in the past or within 5 minutes, send immediately
        if letter.delivery_date <= now + timedelta(minutes=5):
            logger.info(f"Letter {letter.id} is due now or within 5 minutes, sending immediately")
            logger.info(f"Delivery date: {letter.delivery_date}")
            logger.info(f"Current time: {now}")
            send_letter(letter.id)
        else:
            logger.info(f"Letter {letter.id} scheduled for {letter.delivery_date}")
            logger.info(f"Current time: {now}")
            logger.info(f"Time until delivery: {letter.delivery_date - now}")
    except Exception as e:
        logger.error(f"Error scheduling letter {letter.id}: {str(e)}")
        raise
