import io
import logging

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import (
    AppException,
    ErrorCode,
    get_settings,
)
from app.dependencies import (
    Gotenberg,
    get_db_engine,
    get_gotenberg,
    get_redis,
    get_s3,
)
from app.models import Document, DocumentStatus
from app.utils.file_utils import count_pdf_pages, extract_pdf_thumbnail


@shared_task
def generate_document_preview_task(document_id: int):
    """
    Generate preview(pdf) version for document.
    Args:
        document_id: Document.id

    Returns:

    """
    engine = get_db_engine()
    settings = get_settings()
    gotenberg_service = get_gotenberg()
    # redis_client = get_redis()
    s3_client = get_s3()

    with Session(engine) as session:
        document: Document = session.execute(
            select(Document).where(Document.id == document_id)
        ).scalar_one_or_none()

        if document is None:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        elif document.status == DocumentStatus.BANNED:
            raise AppException(ErrorCode.RESOURCE_NOT_AVAILABLE, "Document is banned")

        # change document status to PENDING to avoid any selecting
        document.status = DocumentStatus.PROCESSING
        session.commit()

        # Convert file to PDF & upload to s3
        logging.info("Convert file to PDF....")
        pdf_bytes = gotenberg_service.convert_from_url(
            s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.S3_DOCUMENTS_BUCKET,
                    "Key": document.file_object_key,
                    # add ContentDisposition to let Gotenberg know document type
                    "ResponseContentDisposition": f"attachment; filename=file.{document.file_type}",
                },
            )
        )

        total_pages = count_pdf_pages(pdf_bytes)
        thumbnail_bytes = extract_pdf_thumbnail(pdf_bytes)

        logging.info("Uploading PDF file to S3.....")
        s3_client.upload_fileobj(
            io.BytesIO(pdf_bytes),
            Bucket=settings.S3_DOCUMENTS_BUCKET,
            Key=document.file_preview_object_key,
            ExtraArgs={"ContentType": "application/pdf"},
        )

        logging.info("Uploading PDF thumbnail file to S3.....")
        s3_client.upload_fileobj(
            io.BytesIO(thumbnail_bytes),
            Bucket=settings.S3_DOCUMENTS_BUCKET,
            Key=document.thumbnail_object_key,
            ExtraArgs={"ContentType": "image/png"},
        )

        # Finish change document status
        document.status = DocumentStatus.READY
        document.page_count = total_pages
        session.commit()
