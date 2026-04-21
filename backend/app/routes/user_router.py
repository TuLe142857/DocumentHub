from typing import Annotated

from fastapi import APIRouter, Form, Query

from app.core import (
    APIResponse,
    ErrorCode,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
    build_error_docs,
)
from app.schemas.collection_schema import CollectionQuery, CollectionSchema
from app.schemas.document_schema import (
    DocumentOwnerQuery,
    DocumentPublicQuery,
    DocumentSummarySchema,
)
from app.schemas.user_schema import (
    AvatarUpdateRequest,
    UserProfileUpdateRequest,
    UserPublicProfileSchema,
)
from app.services.auth_service import CurrentUserDep
from app.services.collection_service import CollectionServiceDep
from app.services.document_service import DocumentServiceDep
from app.services.storage_service import StorageServiceDep
from app.services.user_service import UserServiceDep

router = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "/me/profile",
    response_model=ResponseSuccessSchema[UserPublicProfileSchema],
    responses=build_error_docs(ErrorCode.UNAUTHORIZED),
    summary="Get self profile",
)
def get_self_profile(
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    profile = user_service.get_profile_by_id(current_user.id)
    res = UserPublicProfileSchema.model_validate(profile)
    return APIResponse.ok(data=res)


@router.patch(
    "/me/profile",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Update self profile",
)
def update_self_profile(
    body: UserProfileUpdateRequest,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    profile_update_dict = body.model_dump(exclude_unset=True)
    user_service.update_profile(current_user.id, profile_update_dict)
    return APIResponse.ok(message=f"{profile_update_dict}")


@router.put(
    "/me/avatar",
    response_model=ResponseSuccessSchema,
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Update self avatar",
)
def update_avatar(
    form: Annotated[AvatarUpdateRequest, Form(media_type="multipart/form-data")],
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    avatar_file = form.avatar.file
    avatar_content_type = form.avatar.content_type
    user_service.update_avatar(current_user.id, avatar_file, avatar_content_type)
    return APIResponse.ok(data=form.avatar.filename)


@router.get(
    "/me/documents",
    response_model=ResponsePaginationSchema[DocumentSummarySchema],
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        ErrorCode.VALIDATION_ERROR,
    ),
)
def get_self_documents(
    current_user: CurrentUserDep,
    query: Annotated[DocumentOwnerQuery, Query()],
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    docs, total = document_service.get_my_documents(
        user_id=current_user.id, **query.model_dump(exclude_none=True)
    )

    res_data = [
        DocumentSummarySchema.build(doc, storage_service.generate_document_url(doc)[0])
        for doc in docs
    ]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res_data,
    )


@router.get(
    "/me/collections",
    response_model=ResponsePaginationSchema[CollectionSchema],
    responses=build_error_docs(
        ErrorCode.UNAUTHORIZED,
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Get self collections",
)
def get_self_collections(
    current_user: CurrentUserDep,
    query: Annotated[CollectionQuery, Query()],
    collection_service: CollectionServiceDep,
):
    collections, total = collection_service.list_collection(
        owner_id=current_user.id,
        keyword=query.q,
        document_id=query.document_id,
        page=query.page,
        limit=query.limit,
    )
    res_data = [
        CollectionSchema.model_validate(collection) for collection in collections
    ]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res_data,
    )


@router.get(
    "/{username}/profile",
    response_model=ResponseSuccessSchema[UserPublicProfileSchema],
    summary="Select other user's profile",
)
def get_userprofile(
    username: str,
    user_service: UserServiceDep,
):
    profile = user_service.get_profile_by_name(username)
    res = UserPublicProfileSchema.model_validate(profile)
    return APIResponse.ok(data=res)


@router.get(
    "/{username}/documents",
    response_model=ResponsePaginationSchema[DocumentSummarySchema],
    responses=build_error_docs(
        ErrorCode.VALIDATION_ERROR,
    ),
    summary="Select other user's Public && Active documents",
)
def get_user_documents(
    username: str,
    query: Annotated[DocumentPublicQuery, Query()],
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    docs, total = document_service.get_public_documents(
        owner_name=username, **query.model_dump(exclude_none=True)
    )

    res_data = [
        DocumentSummarySchema.build(doc, storage_service.generate_document_url(doc)[0])
        for doc in docs
    ]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res_data,
    )
