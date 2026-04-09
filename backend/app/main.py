from contextlib import asynccontextmanager

from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import (
    get_logger,
    get_settings,
    register_exception_handlers,
    setup_logging,
)
from app.dependencies import get_db_engine, get_gotenberg, get_redis, get_s3
from app.models import *
from app.routes import register_api_router
from app.routes.middlewares import register_middleware

from .worker import create_worker

# create worker for celery task to get config
celery_worker = create_worker()


def create_s3_bucket(bucket_name: str):
    try:
        get_s3().create_bucket(Bucket=bucket_name)
    except ClientError:
        pass


def clear_settings_cache():
    get_settings.cache_clear()
    get_db_engine.cache_clear()
    get_redis.cache_clear()
    get_s3.cache_clear()
    get_gotenberg.cache_clear()


@asynccontextmanager
async def custom_lifespan(app_instance: FastAPI):
    # startup...

    ORMBase.metadata.create_all(get_db_engine())

    settings = get_settings()
    create_s3_bucket(settings.S3_DOCUMENTS_BUCKET)
    create_s3_bucket(settings.S3_IMAGES_BUCKET)

    yield

    # shutdown...


def create_app() -> FastAPI:
    setup_logging()
    logger = get_logger()
    settings = get_settings()

    app_instance = FastAPI(lifespan=custom_lifespan)

    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS allowed: %s", settings.BACKEND_CORS_ORIGINS)

    register_exception_handlers(app_instance)
    register_api_router(app_instance)
    register_middleware(app_instance)

    return app_instance


app = create_app()
