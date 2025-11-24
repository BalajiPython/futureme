from django_apscheduler.jobstores import DjangoJobStore
from django.db import OperationalError
import time
import logging

logger = logging.getLogger(__name__)

class RetryDjangoJobStore(DjangoJobStore):
    def update_job(self, job):
        max_retries = 3
        retry_interval = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                return super().update_job(job)
            except OperationalError as e:
                if "database is locked" in str(e):
                    if attempt < max_retries - 1:
                        logger.warning(f"Database locked, retrying in {retry_interval} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_interval)
                    else:
                        logger.error("Max retries reached for database operation")
                        raise
                else:
                    raise 