from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class LettersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'letters'

    def ready(self):
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
