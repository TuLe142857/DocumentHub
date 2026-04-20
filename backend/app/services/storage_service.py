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

    def _generate_s3_presigned_url(
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

    def generate_document_url(self, document: Document) -> tuple[str, str, str]:
        """
        Args:
            document: Document selected
        Returns:
            tuple[thumbnail_url, preview_url, original_url]

            - thumbnail_url: thumbnail image(image of document's first page)
            - preview_url: preview version(format: PDF)
            - original_url: original version(format: original format)
        """
        settings = get_settings()
        bucket = settings.S3_DOCUMENTS_BUCKET
        base_url = settings.S3_PUBLIC_URL_OVERRIDE
        thumbnail_url = self._generate_s3_presigned_url(
            bucket, document.thumbnail_object_key, base_url=base_url
        )
        preview_url = self._generate_s3_presigned_url(
            bucket,
            document.file_preview_object_key,
            response_content_type="Application/pdf",
            base_url=base_url,
        )
        original_url = self._generate_s3_presigned_url(
            bucket,
            document.file_object_key,
            base_url=base_url,
        )
        return thumbnail_url, preview_url, original_url

    def generate_download_url(self, document: Document) -> tuple[str, str]:
        """
        Generate document download url
        Args:
            document: Document selected to download
        Returns:
            tuple(original_url, pdf_url)

            - original_url: original version(format: PDF)
            - pdf_url: preview version(format: original format)
        """
        settings = get_settings()
        bucket = settings.S3_DOCUMENTS_BUCKET
        base_url = settings.S3_PUBLIC_URL_OVERRIDE

        original_url = self._generate_s3_presigned_url(
            bucket=bucket,
            key=document.file_object_key,
            base_url=base_url,
            extra_params={
                "ResponseContentDisposition": f"attachment; filename={document.title.replace(' ', '')}{document.file_type}"
            },
        )

        pdf_url = self._generate_s3_presigned_url(
            bucket=bucket,
            key=document.file_preview_object_key,
            base_url=base_url,
            response_content_type="Application/pdf",
            extra_params={
                "ResponseContentDisposition": f"attachment; filename={document.title.replace(' ', '')}.pdf"
            },
        )

        return original_url, pdf_url

    def generate_image_url(self, key: str):
        """

        Args:
            key: S3 object key

        Returns:
            url
        """
        settings = get_settings()
        bucket = settings.S3_IMAGES_BUCKET
        base_url = settings.S3_PUBLIC_URL_OVERRIDE

        return self._generate_s3_presigned_url(
            bucket=bucket, key=key, expires_in=24 * 60 * 60, base_url=base_url
        )


def get_storage_service(s3_client: S3Dep) -> StorageService:
    return StorageService(s3_client)


StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
