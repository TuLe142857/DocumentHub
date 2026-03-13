from typing import List

from fastapi import APIRouter, Form, UploadFile
from jinja2.bccache import Bucket

from app.core import APIResponse, ResponseSuccessSchema, get_settings
from app.dependencies import (
    AccessTokenDep,
    DocumentServiceDep,
    OptionalAccessTokenDep,
    S3Dep,
)
from app.schemas.request.document_request import *
from app.schemas.response.document_response import *

router = APIRouter(prefix="/documents", tags=["Document"])


@router.get(
    "/supported_types",
    response_model=ResponseSuccessSchema[DocumentSupportedTypeResponse],
)
def get_supported_types():
    res_data = DocumentSupportedTypeResponse(
        supported_type=get_settings().SUPPORTED_FILE_TYPE
    )
    return APIResponse.ok(data=res_data)


@router.get(
    "",
    response_model=ResponseSuccessSchema,
    summary="Get documents list of current user",
)
def get_document_list(access_token: AccessTokenDep):
    return APIResponse.ok()


@router.get(
    "/{document_id}",
    response_model=ResponseSuccessSchema,
    summary="Get document details",
)
def get_document_details(access_token: OptionalAccessTokenDep, document_id: int):
    # increase document view here
    if access_token:
        # user login
        pass
    else:
        # guest
        pass
    return APIResponse.ok()


@router.get(
    "/{document_id}/download",
    response_model=ResponseSuccessSchema,
    summary="Download document",
)
def download_document(access_token: OptionalAccessTokenDep, document_id: int):
    # increase document download here
    if access_token:
        # user login
        pass
    else:
        # guest
        pass
    return APIResponse.ok()


@router.post(
    "/{document_id}/tags",
    response_model=ResponseSuccessSchema,
    summary="Add tag to document",
)
def add_tag(access_token: AccessTokenDep, document_id: int, tags: list[str]):
    return APIResponse.ok()


@router.delete(
    "/{document_id}/tags",
    response_model=ResponseSuccessSchema,
    summary="Remove tag from document",
)
def remove_tag(access_token: AccessTokenDep, document_id: int, tags: list[str]):
    return APIResponse.ok()


@router.post(
    "/{document_id}/like", response_model=ResponseSuccessSchema, summary="Like document"
)
def like_document(access_token: AccessTokenDep, document_id: int):
    return APIResponse.ok()


@router.delete(
    "/{document_id}/like",
    response_model=ResponseSuccessSchema,
    summary="UnLike document",
)
def unlike_document(access_token: AccessTokenDep, document_id: int):
    return APIResponse.ok()


@router.post("", response_model=ResponseSuccessSchema)
def upload_document(
    body: Annotated[DocumentUploadFormRequest, Form(media_type="multipart/form-data")],
    s3: S3Dep,
):
    import io
    s3.upload_fileobj(
        Fileobj=io.BytesIO(body.file.file.read()),
        Bucket="documents",
        Key=body.title,
        ExtraArgs={
            "ContentType": body.file.content_type
        },
    )
    body.file.file.seek(0)
    data = body.model_dump(exclude=("file", ))
    return APIResponse.ok(message=f"{type(body.file)}", data=data)


@router.put("/{document_id}", response_model=ResponseSuccessSchema)
def update_document(access_token: AccessTokenDep, document_id: int):
    return APIResponse.ok()


@router.delete("/{document_id}", response_model=ResponseSuccessSchema)
def delete_document(access_token: AccessTokenDep, document_id: int):
    return APIResponse.ok()
