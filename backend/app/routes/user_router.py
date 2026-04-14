from typing import Annotated

from fastapi import APIRouter, Form, Query

from app.core import (
    APIResponse,
    PaginationQueryDep,
    ResponsePaginationSchema,
    ResponseSuccessSchema,
)
from app.schemas.collection_schema import CollectionSummaryResponse
from app.schemas.document_schema import DocumentQuery, DocumentSummaryResponse
from app.schemas.user_profile_schema import (
    AvatarUpdateRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from app.services.auth_service import CurrentUserDep, OptionalCurrentUserDep
from app.services.collection_service import CollectionServiceDep
from app.services.document_service import DocumentServiceDep
from app.services.storage_service import StorageServiceDep
from app.services.user_service import UserServiceDep

router = APIRouter(prefix="/users", tags=["UserProfile"])


@router.get("/me/profile", response_model=ResponseSuccessSchema[UserProfileResponse])
def get_self_profile(
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    profile = user_service.get_profile_by_id(current_user.id)
    res = UserProfileResponse.model_validate(profile)
    return APIResponse.ok(data=res)


@router.patch("/me/profile", response_model=ResponseSuccessSchema)
def update_self_profile(
    body: UserProfileUpdateRequest,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    profile_update_dict = body.model_dump(exclude_unset=True)
    user_service.update_profile(current_user.id, profile_update_dict)
    return APIResponse.ok(message=f"{profile_update_dict}")


@router.put("/me/avatar", response_model=ResponseSuccessSchema)
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
    "/me/documents", response_model=ResponsePaginationSchema[DocumentSummaryResponse]
)
def get_self_documents(
    current_user: CurrentUserDep,
    query: Annotated[DocumentQuery, Query()],
    document_service: DocumentServiceDep,
    storage_service: StorageServiceDep,
):
    docs, total = document_service.list_self_documents(
        owner_id=current_user.id,
        page=query.page,
        limit=query.limit,
        status=query.status,
    )
    res_data = [
        DocumentSummaryResponse.build(
            doc, storage_service.generate_presigned_url_for_document(doc)[0]
        )
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
    response_model=ResponsePaginationSchema[CollectionSummaryResponse],
)
def get_self_collections(
    current_user: CurrentUserDep,
    query: PaginationQueryDep,
    collection_service: CollectionServiceDep,
):
    collections, total = collection_service.list_collection(
        owner_id=current_user.id,
        page=query.page,
        limit=query.limit,
    )
    res_data = [
        CollectionSummaryResponse.model_validate(collection)
        for collection in collections
    ]
    return APIResponse.paginate(
        current_page=query.page,
        per_page=query.limit,
        total_items=total,
        data=res_data,
    )


@router.get(
    "/{username}/profile", response_model=ResponseSuccessSchema[UserProfileResponse]
)
def get_userprofile(
    username: str,
    user_service: UserServiceDep,
):
    profile = user_service.get_profile_by_name(username)
    res = UserProfileResponse.model_validate(profile)
    return APIResponse.ok(data=res)


@router.get(
    "/{username}/documents",
    response_model=ResponsePaginationSchema[DocumentSummaryResponse],
)
def get_user_documents(
    username: str,
    pagination: PaginationQueryDep,
    current_user: OptionalCurrentUserDep,
    document_service: DocumentServiceDep,
):
    if current_user is None:
        doc_list, total = document_service.list_public_document(
            owner=username, page=pagination.page, limit=pagination.limit
        )
    else:
        doc_list, total = document_service.get_document_list(
            owner=username,
            viewer=current_user.id,
            page=pagination.page,
            limit=pagination.limit,
        )

    res_data = [DocumentSummaryResponse.model_validate(doc) for doc in doc_list]
    return APIResponse.paginate(
        current_page=pagination.page,
        per_page=pagination.limit,
        total_items=total,
        data=res_data,
    )
