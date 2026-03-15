from functools import lru_cache
from typing import List, Literal

from pydantic import MySQLDsn, RedisDsn, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Literal["dev", "prod"] = "dev"

    SUPPORTED_FILE_TYPE: List[str] = [".doc", ".docx", ".ppt", ".pptx", ".pdf"]

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRES: int = 5 * 60
    JWT_REFRESH_TOKEN_EXPIRES: int = 7 * 24 * 60 * 60

    JWT_ACCESS_COOKIE_NAME: str = "access_token"
    JWT_ACCESS_COOKIE_PATH: str = "/api"

    JWT_REFRESH_COOKIE_NAME: str = "refresh_token"
    JWT_REFRESH_COOKIE_PATH: str = "/api/auth/refresh"

    JWT_COOKIE_SECURE: bool = False
    JWT_COOKIE_SAMESITE: Literal["lax", "strict"] = "lax"

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: SecretStr
    SMTP_SEND_MAIL_FROM: str
    SMTP_USE_TLS: bool

    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: SecretStr

    @computed_field
    @property
    def MYSQL_URL(self) -> MySQLDsn:
        return MySQLDsn.build(
            scheme="mysql+pymysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD.get_secret_value(),
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DATABASE,
        )

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_USER: str
    REDIS_PASSWORD: SecretStr

    def get_redis_url(self, db: int = 0) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            username=self.REDIS_USER,
            password=self.REDIS_PASSWORD.get_secret_value(),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(db),
        )

    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        return self.get_redis_url(0)

    @computed_field
    @property
    def CELERY_BROKER(self) -> RedisDsn:
        return self.get_redis_url(1)

    @computed_field
    @property
    def CELERY_BACKEND(self) -> RedisDsn:
        return self.get_redis_url(1)

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: SecretStr

    S3_DOCUMENTS_BUCKET: str = "documents"
    S3_IMAGES_BUCKET: str = "images"

    GOTENBERG_ENDPOINT: str

    @model_validator(mode="after")
    def validate_secret_variable(self):
        if self.ENVIRONMENT == "dev":
            return self
        for key, value in self.__dict__.items():
            if (
                isinstance(value, SecretStr)
                and value.get_secret_value() == "changethis"
            ):
                raise RuntimeError(
                    f"Please change default value of secret variable `{key}`. Current value: `changethis`"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
