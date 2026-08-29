from __future__ import annotations

import json
import logging
from typing import Any

from django.conf import settings

from .envelope import build_envelope

logger = logging.getLogger(__name__)

_producer = None


def get_producer():
    global _producer
    if _producer is None:
        from confluent_kafka import Producer

        _producer = Producer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': settings.KAFKA_CLIENT_ID,
            'acks': 'all',
        })
    return _producer


def reset_producer() -> None:
    global _producer
    _producer = None


def _delivery_report(err, msg) -> None:
    if err is not None:
        logger.error('Kafka delivery failed for %s: %s', msg.topic() if msg else '?', err)
    else:
        logger.debug(
            'Kafka delivered %s [%s] offset=%s',
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def publish(
    topic_key: str,
    event_type: str,
    organization_id: int,
    payload: dict[str, Any],
    *,
    key: str | None = None,
) -> dict[str, Any]:
    topic = settings.KAFKA_TOPICS[topic_key]
    envelope = build_envelope(event_type, organization_id, payload)
    partition_key = key if key is not None else str(organization_id)

    try:
        producer = get_producer()
        producer.produce(
            topic=topic,
            key=partition_key.encode('utf-8'),
            value=json.dumps(envelope).encode('utf-8'),
            on_delivery=_delivery_report,
        )
        producer.flush(timeout=5)
    except Exception:
        logger.exception(
            'Failed to publish %s to topic %s (org=%s)',
            event_type,
            topic,
            organization_id,
        )
        raise

    return envelope
