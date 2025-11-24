from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class FuturemeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'futureme'

    def ready(self):
        from . import scheduler
        scheduler.start()
        logger.info("Scheduler started from AppConfig ready()")
