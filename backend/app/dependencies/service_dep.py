from typing import Annotated

from fastapi import Depends

from app.core import get_settings
from app.services import *

from .infrastructure_dep import DBSessionDep, RedisDep, S3Dep


def get_jwt_service() -> JWTService:
    return JWTService(
        secret_key=get_settings().JWT_SECRET_KEY.get_secret_value(),
        algorithm=get_settings().JWT_ALGORITHM,
        access_token_expire_seconds=get_settings().JWT_ACCESS_TOKEN_EXPIRES,
        refresh_token_expire_seconds=get_settings().JWT_REFRESH_TOKEN_EXPIRES,
    )


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]


def get_auth_service(
    jwt: JWTServiceDep, redis_client: RedisDep, db_session: DBSessionDep
) -> AuthService:
    return AuthService(
        jwt_service=jwt, redis_client=redis_client, db_session=db_session
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_document_service(
    s3_client: S3Dep, redis_client: RedisDep, db_session: DBSessionDep
) -> DocumentService:
    return DocumentService(
        db_session=db_session,
        redis_client=redis_client,
        s3_client=s3_client,
    )


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
