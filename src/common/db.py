"""PostgreSQL persistence layer for canonical partner events."""

from __future__ import annotations

import json

import psycopg2
from psycopg2.extras import Json

from .config import AppConfig


class PartnerEventRepository:
    def __init__(self, config: AppConfig) -> None:
        self._dsn = {
            "host": config.db_host,
            "port": config.db_port,
            "dbname": config.db_name,
            "user": config.db_user,
            "password": config.db_password,
        }

    def insert_event(self, envelope: dict) -> None:
        with psycopg2.connect(**self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO partner_events (
                        connector,
                        source_type,
                        record_id,
                        received_at,
                        payload
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (connector, record_id) DO UPDATE
                    SET payload = EXCLUDED.payload,
                        received_at = EXCLUDED.received_at
                    """,
                    (
                        envelope["connector"],
                        envelope["source_type"],
                        envelope["record_id"],
                        envelope["received_at"],
                        Json(envelope["payload"]),
                    ),
                )


def ddl() -> str:
    return json.dumps(
        {
            "sql": """
            CREATE TABLE IF NOT EXISTS partner_events (
                connector TEXT NOT NULL,
                source_type TEXT NOT NULL,
                record_id TEXT NOT NULL,
                received_at TIMESTAMPTZ NOT NULL,
                payload JSONB NOT NULL,
                PRIMARY KEY (connector, record_id)
            );
            """
        }
    )
