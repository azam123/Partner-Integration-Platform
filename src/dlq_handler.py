"""Lambda to monitor DLQ traffic and emit CloudWatch metrics."""

from __future__ import annotations

import json
import logging
from typing import Any

from common.alerts import AlertPublisher
from common.config import load_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: Any) -> dict:
    config = load_config()
    alerts = AlertPublisher(config.metric_namespace)

    processed = 0
    for record in event.get("Records", []):
        body = json.loads(record.get("body", "{}"))
        reason = body.get("reason", "unknown")
        connector = "unknown"

        nested = body.get("message")
        if nested:
            try:
                connector = json.loads(nested).get("connector", "unknown")
            except Exception:
                connector = "unknown"

        logger.error("DLQ event connector=%s reason=%s", connector, reason)
        alerts.publish_failure_metric("DLQEvents", connector)
        processed += 1

    return {"processed": processed}
