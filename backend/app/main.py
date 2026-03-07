from fastapi import FastAPI
from app.core import register_exception_handlers
from app.routes import api_router

app = FastAPI()
register_exception_handlers(app)
app.include_router(api_router)