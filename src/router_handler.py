"""Lambda to validate, persist, and route partner events."""

from __future__ import annotations

import json
import logging
from typing import Any

import boto3

from common.alerts import AlertPublisher
from common.config import load_config
from common.db import PartnerEventRepository
from common.models import validate_envelope

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")


def _to_dlq(dlq_url: str, message: str, reason: str) -> None:
    sqs.send_message(
        QueueUrl=dlq_url,
        MessageBody=json.dumps({"reason": reason, "message": message}),
    )


def lambda_handler(event: dict, context: Any) -> dict:
    config = load_config()
    repository = PartnerEventRepository(config)
    alerts = AlertPublisher(config.metric_namespace)

    success = 0
    failed = 0

    for record in event.get("Records", []):
        raw_body = record.get("body", "{}")
        try:
            envelope = json.loads(raw_body)
            validate_envelope(envelope)
            repository.insert_event(envelope)
            success += 1
        except Exception as exc:  # intentionally broad for resilient queue processing
            failed += 1
            connector = "unknown"
            try:
                connector = json.loads(raw_body).get("connector", "unknown")
            except Exception:
                pass

            logger.exception("Failed processing message: %s", exc)
            alerts.publish_failure_metric("InvalidOrFailedEvents", connector)
            _to_dlq(config.dlq_url, raw_body, str(exc))

    return {"success": success, "failed": failed}
