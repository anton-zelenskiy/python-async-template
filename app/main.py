from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.api.health import router as health_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.redis_async import close_redis
from app.core.sentry import init_sentry
from app.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    init_sentry()
    yield
    await close_redis()
    await dispose_engine()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        lifespan=lifespan,
    )

    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    application.include_router(health_router, prefix=settings.API_V1_STR)
    return application


app = create_application()
