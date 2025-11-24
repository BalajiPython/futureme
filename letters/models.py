from django.db import models
from django.conf import settings
import datetime
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class Letter(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    delivery_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    delivery_attempts = models.IntegerField(default=0)
    last_delivery_attempt = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['delivery_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title', 'created_at'],
                name='unique_letter'
            )
        ]
        indexes = [
            models.Index(
                fields=['delivery_date', 'is_delivered', 'delivery_attempts'],
                name='letter_delivery_status_idx'
            ),
            models.Index(
                fields=['author', 'is_delivered'],
                name='letter_author_status_idx'
            ),
            models.Index(
                fields=['last_delivery_attempt'],
                name='letter_last_attempt_idx'
            ),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.email}"

    def mark_as_sent(self):
        """Mark the letter as sent with timestamp"""
        self.is_delivered = True
        self.sent_at = timezone.now()
        self.save(update_fields=['is_delivered', 'sent_at'])

    def increment_delivery_attempt(self):
        """Increment delivery attempts and update last attempt timestamp"""
        self.delivery_attempts += 1
        self.last_delivery_attempt = timezone.now()
        self.save(update_fields=['delivery_attempts', 'last_delivery_attempt'])

    def save(self, *args, **kwargs):
        try:
            logger.info(f"\n=== Saving Letter ===")
            logger.info(f"Author: {self.author.email}")
            logger.info(f"Title: {self.title}")
            logger.info(f"Delivery Date: {self.delivery_date}")
            logger.info(f"Is Delivered: {self.is_delivered}")
            logger.info(f"Delivery Attempts: {self.delivery_attempts}")
            logger.info(f"Last Attempt: {self.last_delivery_attempt}")
            
            super().save(*args, **kwargs)
            
            logger.info(f"Successfully saved letter with ID: {self.id}")
            logger.info("=== End Saving Letter ===\n")
            
        except Exception as e:
            logger.error(f"Error saving letter: {str(e)}", exc_info=True)
            raise

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='letter_profile')

    def __str__(self):
        return f"{self.user.email}'s profile"


# Signal handlers for profile management
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created"""
    if created:
        try:
            Profile.objects.create(user=instance)
        except Exception as e:
            logger.error(f"Error creating user profile for {instance.email}: {str(e)}")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, created=False, **kwargs):
    """Save the profile when the user is saved"""
    # Don't process on create - the create_user_profile handler already handles it
    if created:
        return
    
    try:
        # Only try to save profile if it exists and needs saving
        profile = getattr(instance, 'letter_profile', None)
        if profile is not None:
            profile.save()
    except Exception as e:
        logger.warning(f"Error saving user profile: {str(e)}")