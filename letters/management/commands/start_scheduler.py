from django.core.management.base import BaseCommand
from django.utils import timezone
from letters.tasks import process_due_letters
from letters.models import Letter
import time
import logging
from django.db import connection
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start the APScheduler to process due letters'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting letter scheduler...'))
        
        # Create scheduler
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # Add the job to process due letters every 10 seconds
        scheduler.add_job(
            process_due_letters,
            trigger=IntervalTrigger(seconds=10),
            id='process_due_letters',
            replace_existing=True
        )
        
        try:
            # Start the scheduler
            scheduler.start()
            self.stdout.write(self.style.SUCCESS('Scheduler started successfully'))
            
            # Keep the command running
            while True:
                try:
                    # Check for due letters
                    now = timezone.now()
                    self.stdout.write(f"\nChecking for due letters at {now}")
                    
                    # Get all undelivered letters
                    undelivered = Letter.objects.filter(is_delivered=False)
                    self.stdout.write(f"Total undelivered letters: {undelivered.count()}")
                    
                    # Get due letters
                    due_letters = Letter.objects.filter(
                        delivery_date__lte=now,
                        is_delivered=False
                    ).order_by('delivery_date')
                    
                    self.stdout.write(f"Found {due_letters.count()} due letters")
                    
                    if due_letters.exists():
                        self.stdout.write("Due letters:")
                        for letter in due_letters:
                            self.stdout.write(f"- Letter {letter.id}: {letter.title} (Due: {letter.delivery_date})")
                    
                    # Process due letters
                    process_due_letters()
                    
                    # Close any open database connections
                    connection.close()
                    
                    # Wait for 10 seconds before next check
                    time.sleep(10)
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing letters: {str(e)}'))
                    logger.error(f'Error processing letters: {str(e)}', exc_info=True)
                    time.sleep(10)  # Wait before retrying
                    
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\nStopping scheduler...'))
            scheduler.shutdown()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Fatal error: {str(e)}'))
            logger.error(f'Fatal error: {str(e)}', exc_info=True)
            scheduler.shutdown()