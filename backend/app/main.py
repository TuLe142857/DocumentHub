from fastapi import FastAPI
from app.core import register_exception_handlers, get_db_engine
from app.routes import api_router
from app.models import *

app = FastAPI()

register_exception_handlers(app)

BaseModel.metadata.drop_all(bind=get_db_engine())
BaseModel.metadata.create_all(bind=get_db_engine())

app.include_router(api_router)

from sqlalchemy.schema import CreateTable

for table in BaseModel.metadata.sorted_tables:
    print(CreateTable(table))
