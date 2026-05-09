from django.core.management.base import BaseCommand
from auction.scheduled_tasks import execute_raffle_draw_task

class Command(BaseCommand):
    help = 'Executes the raffle draw for active raffles that have ended.'

    def handle(self, *args, **options):
        self.stdout.write('Manually triggering raffle draw task...')
        execute_raffle_draw_task()
        self.stdout.write(self.style.SUCCESS('Raffle draw task execution completed.'))
