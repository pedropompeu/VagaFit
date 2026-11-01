import pytest

from app.ai.errors import AIProviderError, RetryableAIError
from app.ai.retry import backoff_delay, retry_with_backoff


def test_backoff_delay_grows_and_caps() -> None:
    assert backoff_delay(1, base=1, maximum=30, jitter=1.0) == 1
    assert backoff_delay(3, base=1, maximum=30, jitter=1.0) == 4
    assert backoff_delay(10, base=1, maximum=30, jitter=1.0) == 30
    assert backoff_delay(3, base=1, maximum=30, jitter=0.0) == 2


async def test_retries_then_succeeds() -> None:
    calls = 0
    sleeps: list[float] = []

    async def call() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise RetryableAIError("rate limit")
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    result = await retry_with_backoff(
        call,
        operation="teste",
        max_attempts=5,
        base_delay=1,
        max_delay=30,
        sleep=fake_sleep,
        rand=lambda: 1.0,
    )
    assert result == "ok"
    assert sleeps == [1, 2]


async def test_gives_up_after_max_attempts() -> None:
    async def call() -> str:
        raise RetryableAIError("rate limit")

    async def fake_sleep(_: float) -> None:
        return None

    with pytest.raises(AIProviderError):
        await retry_with_backoff(
            call, operation="teste", max_attempts=2, base_delay=0, max_delay=0, sleep=fake_sleep
        )


async def test_non_retryable_error_propagates() -> None:
    async def call() -> str:
        raise ValueError("bug")

    with pytest.raises(ValueError, match="bug"):
        await retry_with_backoff(call, operation="teste", max_attempts=3, base_delay=0, max_delay=0)
