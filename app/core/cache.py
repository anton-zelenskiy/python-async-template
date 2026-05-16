from collections.abc import Awaitable, Callable
import functools
import hashlib
import json
from typing import ParamSpec, TypeVar

import structlog

from app.core.redis_async import get_redis


logger = structlog.get_logger(__name__)

P = ParamSpec('P')
R = TypeVar('R')


def cached(
    *,
    key_prefix: str,
    ttl: int = 3600,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Cache async function results in Redis using JSON serialization."""

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key_data = {
                'args': args,
                'kwargs': dict(sorted(kwargs.items())),
            }
            key_hash = hashlib.sha256(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
            cache_key = f'{key_prefix}:{func.__name__}:{key_hash}'

            redis = await get_redis()
            try:
                cached_value = await redis.get(cache_key)
                if cached_value is not None:
                    logger.debug('cache_hit', cache_key=cache_key)
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning('cache_get_failed', cache_key=cache_key, error=str(e))

            result = await func(*args, **kwargs)

            try:
                await redis.setex(cache_key, ttl, json.dumps(result, default=str))
                logger.debug('cache_set', cache_key=cache_key, ttl=ttl)
            except Exception as e:
                logger.warning('cache_set_failed', cache_key=cache_key, error=str(e))

            return result

        return wrapper

    return decorator
