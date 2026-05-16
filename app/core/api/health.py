from fastapi import APIRouter
from sqlalchemy import text

from app.core.redis_async import get_redis
from app.db.session import get_session


router = APIRouter(tags=['health'])


@router.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/health/ready')
async def health_ready() -> dict[str, str]:
    async with get_session() as session:
        await session.execute(text('SELECT 1'))

    redis = await get_redis()
    await redis.ping()

    return {'status': 'ready'}
