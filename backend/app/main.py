from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import (
    get_settings,
    register_exception_handlers,
)
from app.dependencies import get_db_engine, get_gotenberg, get_redis, get_s3
from app.models import *
from app.routes import api_router

from .worker import celery_worker


@asynccontextmanager
async def custom_lifespan(app_instance: FastAPI):
    # startup...

    # clear cache to reload setting from env
    # this is for testing with custom config
    get_settings.cache_clear()
    get_db_engine.cache_clear()
    get_redis.cache_clear()
    get_s3.cache_clear()
    get_gotenberg.cache_clear()

    ORMBase.metadata.create_all(get_db_engine())
    try:
        get_s3().create_bucket(Bucket=get_settings().S3_DOCUMENTS_BUCKET)
    except Exception:
        # Bucket already exits
        pass

    yield

    # shutdown...


def create_app() -> FastAPI:
    app_instance = FastAPI(lifespan=custom_lifespan)

    register_exception_handlers(app_instance)

    app_instance.include_router(api_router)

    return app_instance


app = create_app()
