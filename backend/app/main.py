from fastapi import FastAPI

from app.core import get_db_engine, register_exception_handlers
from app.models import *
from app.routes import api_router

from .celery_worker import celery_worker

app = FastAPI()

register_exception_handlers(app)

BaseModel.metadata.drop_all(bind=get_db_engine())
BaseModel.metadata.create_all(bind=get_db_engine())

app.include_router(api_router)

from sqlalchemy.schema import CreateTable

for table in BaseModel.metadata.sorted_tables:
    print(CreateTable(table))
