"""Configuration helpers for Lambda handlers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConnectorConfig:
    name: str
    url: str
    headers: dict[str, str]


@dataclass(frozen=True)
class AppConfig:
    ingress_queue_url: str
    dlq_url: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    metric_namespace: str
    max_retries: int
    backoff_base_seconds: float
    connectors: list[ConnectorConfig]


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _load_connectors(raw: str | None) -> list[ConnectorConfig]:
    if not raw:
        return []

    payload: list[dict[str, Any]] = json.loads(raw)
    connectors: list[ConnectorConfig] = []

    for item in payload:
        connectors.append(
            ConnectorConfig(
                name=item["name"],
                url=item["url"],
                headers=item.get("headers", {}),
            )
        )

    return connectors


def load_config() -> AppConfig:
    return AppConfig(
        ingress_queue_url=_required("INGRESS_QUEUE_URL"),
        dlq_url=_required("DLQ_URL"),
        db_host=_required("DB_HOST"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=_required("DB_NAME"),
        db_user=_required("DB_USER"),
        db_password=_required("DB_PASSWORD"),
        metric_namespace=os.getenv("APP_NAMESPACE", "PartnerIntegration"),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        backoff_base_seconds=float(os.getenv("BACKOFF_BASE_SECONDS", "0.5")),
        connectors=_load_connectors(os.getenv("CONNECTOR_CONFIG_JSON")),
    )
