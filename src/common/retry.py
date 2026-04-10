"""Retry helpers with exponential backoff and jitter."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def with_retry(
    func: Callable[[], T],
    retries: int,
    backoff_base_seconds: float,
    retry_exceptions: tuple[type[Exception], ...],
) -> T:
    attempt = 0

    while True:
        try:
            return func()
        except retry_exceptions:
            if attempt >= retries:
                raise
            sleep_seconds = (backoff_base_seconds * (2**attempt)) + random.uniform(0, backoff_base_seconds)
            time.sleep(sleep_seconds)
            attempt += 1
