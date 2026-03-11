from redis import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

from .jwt_service import JWTService


class AuthService:
    def __init__(
        self, jwt_service: JWTService, redis_client: Redis, db_session: Session
    ):
        self.jwt_service = jwt_service
        self.redis_client = redis_client
        self.db_session = db_session

    def __generate_access_token(self):
        pass

    def __generate_refresh_token(self):
        pass

    def request_registration(self, email: str):
        pass

    def verify_registration(self):
        pass

    def complete_registration(self):
        pass

    def login(self):
        pass

    def refresh_access_token(self):
        pass

    def forgot_password(self):
        pass

    def reset_password(self):
        pass
