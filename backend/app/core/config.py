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

    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        return self.get_redis_url(0)

    def get_redis_url(self, db: int = 0) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            username=self.REDIS_USER,
            password=self.REDIS_PASSWORD.get_secret_value(),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(db),
        )

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: SecretStr

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


settings = Settings()
