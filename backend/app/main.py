from contextlib import asynccontextmanager

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
    s3 = get_s3()
    logger = get_logger()
    try:
        s3.create_bucket(Bucket=bucket_name)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        logger.debug(f"When create Bucket '{bucket_name}': BucketAlreadyOwnedByYou")
    except s3.exceptions.BucketAlreadyExists:
        logger.error(
            f"When create Bucket '{bucket_name}': Bucket already exists but not Owned by You"
        )
        raise
    except Exception as e:
        logger.error(
            f"Something went wrong when creating S3 Bucket '{bucket_name}' {str(e)}"
        )
        raise


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
    logger = get_logger()
    settings = get_settings()
    res = get_s3().list_buckets()
    logger.debug(f"Buckets in S3: {res['Buckets']}")

    create_s3_bucket(settings.S3_DOCUMENTS_BUCKET)
    create_s3_bucket(settings.S3_IMAGES_BUCKET)

    yield

    # shutdown...


def create_app() -> FastAPI:
    setup_logging()
    logger = get_logger()
    settings = get_settings()

    app_instance = FastAPI(
        lifespan=custom_lifespan,
        summary="Hello World!",
        description="Some description...",
    )

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
