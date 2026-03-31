from typing import Annotated
from urllib.parse import urlparse

from fastapi import Depends
from mypy_boto3_s3 import S3Client

from app.core import get_settings
from app.dependencies import S3Dep
from app.models import Document


class StorageService:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    def generate_s3_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 5 * 60,
        client_method: str = "get_object",
        response_content_type: str | None = None,
        extra_params: dict | None = None,
        base_url: str | None = None,
    ) -> str:
        params = extra_params or {}
        params["Bucket"] = bucket
        params["Key"] = key
        if response_content_type:
            params["ResponseContentType"] = response_content_type

        url = self.s3_client.generate_presigned_url(
            ClientMethod=client_method,
            Params=params,
            ExpiresIn=expires_in,
        )

        if base_url is not None:
            parsed_url = urlparse(url)
            final_url = base_url + parsed_url.path + "?" + parsed_url.query
            return final_url
        else:
            return url

    def generate_presigned_url_for_document(
        self, document: Document
    ) -> tuple[str, str, str]:
        """
        Args:
            document: Document to generate presigned url
        Returns: tuple[thumbnail_url, preview_url, original_url]
        """
        settings = get_settings()
        bucket = settings.S3_DOCUMENTS_BUCKET
        base_url = settings.S3_PUBLIC_URL_OVERRIDE
        thumbnail_url = self.generate_s3_presigned_url(
            bucket, document.thumbnail_object_key, base_url=base_url
        )
        preview_url = self.generate_s3_presigned_url(
            bucket,
            document.file_preview_object_key,
            response_content_type="Application/pdf",
            base_url=base_url,
        )
        original_url = self.generate_s3_presigned_url(
            bucket,
            document.file_object_key,
            base_url=base_url,
        )
        return thumbnail_url, preview_url, original_url


def get_storage_service(s3_client: S3Dep) -> StorageService:
    return StorageService(s3_client)


StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
