from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
import uuid
from django.contrib.auth.hashers import make_password

class PendingRegistration(models.Model):
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = self.created_at + datetime.timedelta(minutes=10)
        return timezone.now() > expiration_time

class Letter(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    delivery_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ['delivery_date']

    def __str__(self):
        return f"{self.title} - {self.delivery_date}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email}'s profile"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
