from django.core.management.base import BaseCommand

from core.events.consumer import EventConsumer


class Command(BaseCommand):
    help = (
        'Consume CRM domain events from Kafka/Redpanda and run handlers. '
        'Run alongside the web server: python manage.py consume_events'
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Kafka event consumer...'))
        self.stdout.write(
            'Ensure Redpanda/Kafka is up (docker compose up -d) before consuming.'
        )
        consumer = EventConsumer()
        consumer.run()
