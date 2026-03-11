from typing import Annotated

from fastapi import Depends

from app.core import settings
from app.services import *

from .infrastructure_dep import DBSessionDep, RedisDep, S3Dep


def get_jwt_service() -> JWTService:
    return JWTService(
        secret_key=settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_seconds=settings.JWT_ACCESS_TOKEN_EXPIRES,
        refresh_token_expire_seconds=settings.JWT_REFRESH_TOKEN_EXPIRES,
    )


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]


def get_auth_service(
    jwt: JWTServiceDep, redis_client: RedisDep, db_session: DBSessionDep
) -> AuthService:
    return AuthService(
        jwt_service=jwt, redis_client=redis_client, db_session=db_session
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
