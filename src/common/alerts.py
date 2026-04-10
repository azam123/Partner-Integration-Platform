"""CloudWatch metric utilities for operational alerting."""

from __future__ import annotations

import boto3


class AlertPublisher:
    def __init__(self, namespace: str) -> None:
        self.namespace = namespace
        self._cloudwatch = boto3.client("cloudwatch")

    def publish_failure_metric(self, metric_name: str, connector: str, count: int = 1) -> None:
        self._cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": [{"Name": "Connector", "Value": connector}],
                    "Value": float(count),
                    "Unit": "Count",
                }
            ],
        )
