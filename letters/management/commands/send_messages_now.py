from django.core.management.base import BaseCommand
from futureme.scheduler import send_scheduled_messages

class Command(BaseCommand):
    help = 'Manually trigger message sending'
    
    def handle(self, *args, **options):
        self.stdout.write('Manually sending scheduled messages...')
        send_scheduled_messages()
        self.stdout.write('Done!')