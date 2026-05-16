import structlog

from app.celery_app import celery_app
from app.core.redis_async import get_redis
from app.tasks.asyncio_runner import run


logger = structlog.get_logger(__name__)


@celery_app.task(name='app.tasks.example.ping')
def ping() -> str:
    logger.info('celery_ping')
    return 'pong'


async def _redis_ping() -> str:
    redis = await get_redis()
    result = await redis.ping()
    return 'pong' if result else 'fail'


@celery_app.task(name='app.tasks.example.ping_redis_async')
def ping_redis_async() -> str:
    return run(_redis_ping())
