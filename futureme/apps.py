# futureme/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger('futureme.scheduler')

class FuturemeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'futureme'
    
    def ready(self):
        """
        Don't start scheduler here - it's started from letters.apps.LettersConfig
        """
        # Scheduler is initialized in letters/apps.py to avoid duplicate instances
        pass

