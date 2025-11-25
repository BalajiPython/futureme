from django.apps import AppConfig
import logging
import os
import sys

logger = logging.getLogger(__name__)

class LettersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'letters'

    def ready(self):
        # Skip scheduler initialization during:
        # - Management commands (migrate, etc.)
        # - Testing
        # - Non-main processes
        
        if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'makemigrations', 'test', 'collectstatic']:
            return
            
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
        
        # Only start scheduler in production (Render) or when explicitly enabled
        if os.getenv('DEBUG') == 'True':
            logger.info("Running in DEBUG mode - scheduler disabled for local development")
            return
            
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
