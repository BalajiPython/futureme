from django.core.management.base import BaseCommand
from futureme.scheduler import check_scheduler_status, get_scheduled_jobs
from letters.models import Letter
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks the status of the APScheduler'

    def handle(self, *args, **options):
        try:
            check_scheduler_status()
            jobs = get_scheduled_jobs()
            self.stdout.write(f'Found {len(jobs)} scheduled jobs:')
            for job in jobs:
                self.stdout.write(f'  - {job.id}: Next run at {job.next_run_time}')
        except Exception as e:
            logger.error(f"Failed to check scheduler status: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Failed to check scheduler status: {str(e)}'))

        # Check pending letters
        now = timezone.now()
        pending_letters = Letter.objects.filter(is_delivered=False)
        due_letters = Letter.objects.filter(
            delivery_date__lte=now,
            is_delivered=False
        )
        
        self.stdout.write(f'\nPending letters: {pending_letters.count()}')
        self.stdout.write(f'Due letters: {due_letters.count()}')
        
        if due_letters.exists():
            self.stdout.write('\nDue letters:')
            for letter in due_letters[:5]:  # Show first 5
                self.stdout.write(f'  - ID {letter.id}: {letter.title} (due: {letter.delivery_date})')
