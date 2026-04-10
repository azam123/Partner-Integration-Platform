"""Lambda to ingest data from third-party connectors and publish to SQS ingress queue."""

from __future__ import annotations

import json
import logging
from typing import Any

import boto3
import requests

from common.config import ConnectorConfig, load_config
from common.models import build_envelope
from common.retry import with_retry

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")


def _fetch_connector_data(connector: ConnectorConfig, retries: int, backoff: float) -> list[dict[str, Any]]:
    def _request() -> list[dict[str, Any]]:
        response = requests.get(connector.url, headers=connector.headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "records" in data and isinstance(data["records"], list):
            return data["records"]
        raise ValueError(f"Unexpected payload for connector={connector.name}")

    return with_retry(_request, retries=retries, backoff_base_seconds=backoff, retry_exceptions=(requests.RequestException,))


def lambda_handler(event: dict, context: Any) -> dict:
    config = load_config()
    published = 0

    for connector in config.connectors:
        logger.info("Polling connector=%s", connector.name)
        records = _fetch_connector_data(connector, config.max_retries, config.backoff_base_seconds)
        for record in records:
            envelope = build_envelope(connector.name, "partner_api", record)
            sqs.send_message(
                QueueUrl=config.ingress_queue_url,
                MessageBody=json.dumps(envelope.to_dict()),
            )
            published += 1

    return {"published": published}
