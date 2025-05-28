# futureme/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger('futureme.scheduler')

class FuturemeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'futureme'
    
    def ready(self):
        """
        Start the scheduler when Django starts
        """
        # Only start scheduler in the main process (not in migrations, etc.)
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
            
        try:
            from . import scheduler
            scheduler.start_scheduler()
            logger.info("Scheduler initialized from apps.py")
        except Exception as e:
            logger.error(f"Failed to start scheduler in apps.py: {str(e)}")

