from __future__ import annotations

import json
import logging
import signal
import time

from django.conf import settings

from .handlers.registry import dispatch, register_handlers

logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(self):
        from confluent_kafka import Consumer

        register_handlers()
        self._running = True
        topics = list(settings.KAFKA_TOPICS.values())
        self._consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_CONSUMER_GROUP,
            'client.id': f'{settings.KAFKA_CLIENT_ID}-consumer',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })
        self._consumer.subscribe(topics)
        logger.info('Subscribed to topics: %s', topics)

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        logger.info('Event consumer started')
        try:
            while self._running:
                msg = self._consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error('Consumer error: %s', msg.error())
                    continue

                try:
                    envelope = json.loads(msg.value().decode('utf-8'))
                    dispatch(envelope)
                    self._consumer.commit(asynchronous=False)
                except Exception:
                    logger.exception(
                        'Failed handling message topic=%s partition=%s offset=%s; skipping',
                        msg.topic(),
                        msg.partition(),
                        msg.offset(),
                    )
                    # Commit to avoid poison-pill loops; handlers must be idempotent.
                    try:
                        self._consumer.commit(asynchronous=False)
                    except Exception:
                        logger.exception('Failed to commit offset after handler error')
                    time.sleep(0.1)
        finally:
            self._consumer.close()
            logger.info('Event consumer stopped')

    def _handle_signal(self, signum, frame) -> None:
        logger.info('Received signal %s, shutting down consumer', signum)
        self.stop()
