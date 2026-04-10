# Serverless Partner Integration Platform

A production-ready reference implementation for ingesting partner data (ERP and e-commerce connectors), validating payloads, routing events, and persisting standardized records in PostgreSQL with resilient operations.

## Architecture

- **Ingestion Lambda (`ingest_handler`)**
  - Pulls records from third-party APIs (ERP/e-commerce connectors).
  - Uses retry with exponential backoff and jitter for transient failures.
  - Publishes normalized envelopes to an SQS ingress queue.

- **Router Lambda (`router_handler`)**
  - Triggered by ingress SQS.
  - Validates envelope + payload shape.
  - Persists valid records to PostgreSQL.
  - Routes invalid records or processing failures to a DLQ.

- **DLQ Monitor Lambda (`dlq_handler`)**
  - Triggered by DLQ.
  - Emits CloudWatch metrics and logs actionable context for triage.

- **CloudWatch Alerting**
  - Alarm on DLQ backlog.
  - Custom metric for failed/invalid events.

## Project Structure

```text
src/
  common/
    alerts.py
    config.py
    db.py
    models.py
    retry.py
  ingest_handler.py
  router_handler.py
  dlq_handler.py
template.yaml
requirements.txt
tests/
```

## Environment Variables

| Name | Description |
|---|---|
| `CONNECTOR_CONFIG_JSON` | JSON array of connectors to poll (`name`, `url`, optional `headers`) |
| `INGRESS_QUEUE_URL` | SQS URL for normalized envelopes |
| `DLQ_URL` | SQS URL for dead-letter events |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL connection settings |
| `APP_NAMESPACE` | CloudWatch metric namespace (default: `PartnerIntegration`) |
| `MAX_RETRIES` | Retry count for outbound API calls (default: 3) |
| `BACKOFF_BASE_SECONDS` | Retry backoff base seconds (default: 0.5) |

## Local Testing

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Deploy (AWS SAM)

```bash
sam build
sam deploy --guided
```

