from app.core.retry import retry


@retry(max_attempts=3, start_delay=0.01)
async def flaky() -> str:
    flaky.attempts += 1
    if flaky.attempts < 3:
        raise ValueError('not yet')
    return 'ok'


flaky.attempts = 0


async def test_retry_succeeds_after_failures():
    flaky.attempts = 0
    result = await flaky()
    assert result == 'ok'
    assert flaky.attempts == 3
