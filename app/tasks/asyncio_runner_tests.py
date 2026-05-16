import asyncio

import pytest

from app.tasks.asyncio_runner import run


async def _return_value() -> int:
    return 42


def test_run_executes_coroutine():
    assert run(_return_value()) == 42


def test_run_raises_when_called_from_running_loop():
    async def inner():
        coro = _return_value()
        try:
            with pytest.raises(RuntimeError, match='running event loop'):
                run(coro)
        finally:
            coro.close()

    asyncio.run(inner())
