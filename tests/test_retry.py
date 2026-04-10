from common.retry import with_retry


class RetryableError(RuntimeError):
    pass


def test_with_retry_eventually_succeeds():
    state = {"count": 0}

    def flaky() -> str:
        state["count"] += 1
        if state["count"] < 3:
            raise RetryableError("transient")
        return "ok"

    assert with_retry(flaky, retries=3, backoff_base_seconds=0.0, retry_exceptions=(RetryableError,)) == "ok"
