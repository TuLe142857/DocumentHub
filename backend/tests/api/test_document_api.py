import pytest
from fastapi.testclient import TestClient

from app.core import ErrorCode, get_settings
from app.models import *
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import (
    role_user,
    user,
    auth_client,
    user_factory,
    document_factory,
    collection_factory,
category_factory,
    TEST_PASSWORD,
)


class TestGetDocumentMeta:
    def test_get_supported_types(self, client):
        supported_types = assert_response_ok(client.get("/documents/supported_types"))
        assert isinstance(supported_types, list)
        assert all(isinstance(t, str) for t in supported_types)

    def test_get_max_upload_size(self, client):
        max_size_bytes = assert_response_ok(client.get("/documents/max_size"))
        assert isinstance(max_size_bytes, int)
        assert max_size_bytes > 0


class TestUploadDocument:
    @pytest.mark.parametrize(
        ["title", "file_test", "category_name", "visibility", "desc", "tags"],
        [
            [
                "DocumentTitle",
                "test_doc.docx",
                "Category",
                DocumentVisibility.PUBLIC,
                None,
                None,
            ],
            [
                "DocumentTitle",
                "test_ppt.pptx",
                "Category",
                DocumentVisibility.PUBLIC,
                None,
                ["tag1", "tag_2"],
            ],
            [
                "DocumentTitle",
                "test_pdf.pdf",
                "Category",
                DocumentVisibility.PUBLIC,
                "DocumentDescription",
                None,
            ],
            [
                "DocumentTitle",
                "test_pdf.pdf",
                "Category",
                DocumentVisibility.PUBLIC,
                "DocumentDescription",
                ["tag1", "tag_2"],
            ],
        ],
    )
    def test_success(
        self,
        db_session,
        auth_client: TestClient,
        title: str,
        file_test: str,
        category_name: str,
        visibility: DocumentVisibility,
        desc: str | None,
        tags: list[str] | None,
    ):
        print(category_name)
        category = Category(name=category_name)
        db_session.add(category)
        db_session.commit()

        data: dict[str, str | list[str]] = {
            "title": title,
            "category_id": str(category.id),
            "visibility": visibility.name,
        }

        if desc is not None:
            data["desc"] = desc
        if tags is not None:
            data["tags"] = tags

        with open(f"tests/files/{file_test}", "rb") as f:
            assert_response_ok(
                auth_client.post(
                    "/documents",
                    data=data,
                    files={
                        "file": (file_test, f),
                    },
                )
            )

    def test_unauthenticated(self, db_session, client):
        category = Category(name="test_category")
        assert_response_error(
            client.post(
                "/documents",
                data={
                    "title": "test_title",
                    "category_id": str(category.id),
                },
                files={"file": ("file.pdf", b"fake_binary")},
            ),
            ErrorCode.UNAUTHORIZED,
        )

    def test_duplicate_title(self, auth_client, user, document_factory):
        category = Category(name="test_category")
        document = document_factory.create(owner=user, category=category)
        assert_response_error(
            auth_client.post(
                "/documents",
                data={
                    "title": document.title,
                    "category_id": str(category.id),
                },
                files={"file": ("file.pdf", b"fake_binary")},
            ),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    def test_unsupported_file_type(self, auth_client, user, document_factory):
        category = Category(name="test_category")
        assert_response_error(
            auth_client.post(
                "/documents",
                data={
                    "title": "test_title",
                    "category_id": str(category.id),
                },
                files={"file": ("file.html", b"fake_binary")},
            ),
            ErrorCode.VALIDATION_ERROR,
        )

    def test_file_to_large(self, auth_client):
        category = Category(name="test_category")

        size_large = get_settings().MAX_FILE_SIZE * 2
        assert_response_error(
            auth_client.post(
                "/documents",
                data={
                    "title": "test_title",
                    "category_id": str(category.id),
                },
                files={"file": ("file.pdf", b"b" * size_large)},
            ),
            ErrorCode.FILE_TOO_LARGE,
        )

    def test_category_not_found(self, auth_client):
        assert_response_error(
            auth_client.post(
                "/documents",
                data={
                    "title": "test_title",
                    "category_id": "1",
                },
                files={"file": ("file.pdf", b"fake_binary")},
            ),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    @pytest.mark.parametrize(
        "tags", [[""], ["CapitalizeTags"], ["SpecialChar_&^%"], ["Contain space"]]
    )
    def test_invalid_tags(self, auth_client, tags):
        category = Category(name="test_category")
        assert_response_error(
            auth_client.post(
                "/documents",
                data={
                    "title": "test_title",
                    "category_id": str(category.id),
                    "tags": tags,
                },
                files={"file": ("file.pdf", b"fake_binary")},
            ),
            ErrorCode.VALIDATION_ERROR,
        )


class TestGetDocumentDetails:
    # --- Guest (Unauthenticated) ---
    def test_guest_can_get_public_document(self, client, user, document_factory):
        public_doc = document_factory.create(
            owner=user, category=Category(name="test_category")
        )
        assert_response_ok(
            client.get(f"/documents/{public_doc.id}"),
        )

    def test_guest_cannot_get_private_document(self, client, user, document_factory):
        private_doc = document_factory.create(
            owner=user, category=Category(name="test_category"), visibility=DocumentVisibility.PRIVATE
        )
        assert_response_error(
            client.get(f"/documents/{private_doc.id}"),
            ErrorCode.FORBIDDEN,
        )

    # --- Owner (Authenticated - Self) ---
    def test_owner_can_get_own_public_document(
        self, auth_client, user, document_factory
    ):
        public_doc = document_factory.create(
            owner=user, category=Category(name="test_category")
        )
        assert_response_ok(
            auth_client.get(f"/documents/{public_doc.id}"),
        )

    def test_owner_can_get_own_private_document(
        self, auth_client, user, document_factory
    ):
        private_doc = document_factory.create(
            owner=user,
            category=Category(name="test_category"),
            visibility=DocumentVisibility.PRIVATE,
        )
        assert_response_ok(
            auth_client.get(f"/documents/{private_doc.id}"),
        )

    # --- Other User (Authenticated - Others) ---
    def test_user_can_get_others_public_document(
        self, auth_client, user, document_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other_user@mail", TEST_PASSWORD)
        others_public_doc = document_factory.create(
            owner=other_user, category=Category(name="test_category")
        )
        assert_response_ok(
            auth_client.get(f"/documents/{others_public_doc.id}"),
        )

    def test_user_cannot_get_others_private_document(
        self, auth_client, user, document_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other_user@mail", TEST_PASSWORD)
        others_private_doc = document_factory.create(
            owner=other_user,
            category=Category(name="test_category"),
            visibility=DocumentVisibility.PRIVATE,
        )
        assert_response_error(
            auth_client.get(f"/documents/{others_private_doc.id}"),
            ErrorCode.FORBIDDEN,
        )

    # --- Edge Cases ---
    def test_document_not_found(self, client):
        assert_response_error(
            client.get(f"/documents/{3355}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )


class TestUpdateDocument:

    # ------------------------------------------------------------------
    # Success cases
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("payload", [
        {"title": "New Title"},
        {"desc": "New description"},
        {"visibility": DocumentVisibility.PRIVATE.name},
        {"title": "New Title", "desc": "New description"},
        {"title": "New Title", "visibility": DocumentVisibility.PRIVATE.name},
        {"title": "New Title", "desc": "New desc", "visibility": DocumentVisibility.PRIVATE.name},
    ])
    def test_owner_can_update(self, auth_client, user, document_factory, category_factory, payload):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_ok(
            auth_client.patch(f"/documents/{doc.id}", json=payload)
        )

        # check after update


    # ------------------------------------------------------------------
    # Permission
    # ------------------------------------------------------------------

    def test_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.patch(f"/documents/{doc.id}", json={"title": "New Title"}),
            ErrorCode.UNAUTHORIZED,
        )

    def test_stranger_cannot_update(self, auth_client, document_factory, category_factory, user_factory):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        doc = document_factory.create(owner=other_user, category=category_factory.create())
        assert_response_error(
            auth_client.patch(f"/documents/{doc.id}", json={"title": "New Title"}),
            ErrorCode.FORBIDDEN,
        )

    # ------------------------------------------------------------------
    # Not found
    # ------------------------------------------------------------------

    def test_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.patch("/documents/99999", json={"title": "New Title"}),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_duplicate_title(self, auth_client, user, document_factory, category_factory):
        category = category_factory.create()
        existing_doc = document_factory.create(owner=user, category=category, title="Existing Title")
        target_doc = document_factory.create(owner=user, category=category, title="Other Title")
        assert_response_error(
            auth_client.patch(f"/documents/{target_doc.id}", json={"title": existing_doc.title}),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    def test_category_not_found(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            auth_client.patch(f"/documents/{doc.id}", json={"category_id": 99999}),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    @pytest.mark.parametrize("tags", [
        [""],
        ["CapitalizeTags"],
        ["special_char_&^%"],
        ["contain space"],
    ])
    def test_invalid_tags(self, auth_client, user, document_factory, category_factory, tags):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            auth_client.patch(f"/documents/{doc.id}", json={"tags": tags}),
            ErrorCode.VALIDATION_ERROR,
        )


class TestDeleteDocument:
    """
    DELETE /documents/{document_id} — Move to trash
    """

    def test_success(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_ok(
            auth_client.delete(f"/documents/{doc.id}")
        )

    def test_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.delete(f"/documents/{doc.id}"),
            ErrorCode.UNAUTHORIZED,
        )

    def test_stranger_cannot_delete(self, auth_client, document_factory, category_factory, user_factory):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        doc = document_factory.create(owner=other_user, category=category_factory.create())
        assert_response_error(
            auth_client.delete(f"/documents/{doc.id}"),
            ErrorCode.FORBIDDEN,
        )

    def test_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.delete("/documents/99999"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

class TestRestoreDocument:
    def test_success(
            self, auth_client, user, document_factory, category_factory
    ):
        doc = document_factory.create(owner=user, category=category_factory.create())
        auth_client.delete(f"/documents/{doc.id}")
        assert_response_ok(
            auth_client.post(f"/documents/{doc.id}/restore")
        )

    def test_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.post(f"/documents/{doc.id}/restore"),
            ErrorCode.UNAUTHORIZED,
        )

    def test_stranger_cannot_restore(
            self, auth_client, document_factory, category_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        doc = document_factory.create(owner=other_user, category=category_factory.create())
        assert_response_error(
            auth_client.post(f"/documents/{doc.id}/restore"),
            ErrorCode.FORBIDDEN,
        )

    def test_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.post("/documents/99999/restore"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

class TestDocumentTags:
    """
    PUT    /documents/{document_id}/tags  — thêm tag
    DELETE /documents/{document_id}/tags  — xóa tag
    """

    # ------------------------------------------------------------------
    # PUT — Add tag
    # ------------------------------------------------------------------

    def test_add_tag_success(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_ok(
            auth_client.put(f"/documents/{doc.id}/tags", json={"tag_name": "newtag"})
        )

    def test_add_tag_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.put(f"/documents/{doc.id}/tags", json={"tag_name": "newtag"}),
            ErrorCode.UNAUTHORIZED,
        )

    def test_stranger_cannot_add_tag(
        self, auth_client, document_factory, category_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        doc = document_factory.create(owner=other_user, category=category_factory.create())
        assert_response_error(
            auth_client.put(f"/documents/{doc.id}/tags", json={"tag_name": "newtag"}),
            ErrorCode.FORBIDDEN,
        )

    def test_add_tag_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.put("/documents/99999/tags", json={"tag_name": "newtag"}),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    @pytest.mark.parametrize("tag_name", [
        "",
        "CapitalizeTag",
        "special_&^%",
        "contain space",
    ])
    def test_add_invalid_tag_name(self, auth_client, user, document_factory, category_factory, tag_name):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            auth_client.put(f"/documents/{doc.id}/tags", json={"tag_name": tag_name}),
            ErrorCode.VALIDATION_ERROR,
        )

    # ------------------------------------------------------------------
    # DELETE — Remove tag
    # ------------------------------------------------------------------

    def test_remove_tag_success(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        auth_client.put(f"/documents/{doc.id}/tags", json={"tag_name": "newtag"})
        assert_response_ok(
            auth_client.request("DELETE", f"/documents/{doc.id}/tags", json={"tag_name": "newtag"})
        )

    def test_remove_tag_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.request("DELETE", f"/documents/{doc.id}/tags", json={"tag_name": "newtag"}),
            ErrorCode.UNAUTHORIZED,
        )

    def test_stranger_cannot_remove_tag(
        self, auth_client, document_factory, category_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        doc = document_factory.create(owner=other_user, category=category_factory.create())
        assert_response_error(
            auth_client.request("DELETE", f"/documents/{doc.id}/tags", json={"tag_name": "newtag"}),
            ErrorCode.FORBIDDEN,
        )

    def test_remove_tag_document_not_found(self, auth_client:TestClient):
        assert_response_error(
            auth_client.request(
                "DELETE",
                f"/documents/{999}/tags",
                json={"tag_name": "newtag"},
            ) ,
            ErrorCode.RESOURCE_NOT_FOUND,
        )


class TestDocumentLike:
    """
    PUT    /documents/{document_id}/like  — like
    DELETE /documents/{document_id}/like  — unlike
    """

    # ------------------------------------------------------------------
    # PUT — Like
    # ------------------------------------------------------------------

    def test_like_document(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())

        like_count_before = assert_response_ok(auth_client.get(f"/documents/{doc.id}"))["like_count"]
        assert_response_ok(
            auth_client.put(f"/documents/{doc.id}/like")
        )
        like_count_after = assert_response_ok(auth_client.get(f"/documents/{doc.id}"))["like_count"]
        assert like_count_after == like_count_before + 1


    def test_like_document_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.put(f"/documents/{doc.id}/like"),
            ErrorCode.UNAUTHORIZED,
        )

    def test_like_private_document_as_stranger(
        self, auth_client, document_factory, category_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        private_doc = document_factory.create(
            owner=other_user,
            category=category_factory.create(),
            visibility=DocumentVisibility.PRIVATE,
        )
        assert_response_error(
            auth_client.put(f"/documents/{private_doc.id}/like"),
            ErrorCode.FORBIDDEN,
        )

    def test_like_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.put("/documents/99999/like"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    # ------------------------------------------------------------------
    # DELETE — Unlike
    # ------------------------------------------------------------------

    def test_unlike_document(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        auth_client.put(f"/documents/{doc.id}/like")

        like_count_before = assert_response_ok(auth_client.get(f"/documents/{doc.id}"))["like_count"]
        assert_response_ok(
            auth_client.delete(f"/documents/{doc.id}/like")
        )
        like_count_after = assert_response_ok(auth_client.get(f"/documents/{doc.id}"))["like_count"]

        assert like_count_after == like_count_before - 1

    def test_unlike_document_unauthenticated(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.delete(f"/documents/{doc.id}/like"),
            ErrorCode.UNAUTHORIZED,
        )

    def test_unlike_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.delete("/documents/99999/like"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )


class TestDownloadDocument:
    """
    GET /documents/{document_id}/download?format=.pdf
    format: query param, optional, default='.pdf'
    """

    @staticmethod
    def _do_download_success(client: TestClient, doc_id: int, assert_download_count:bool = True):
        if assert_download_count:
            download_count_before = assert_response_ok(client.get(f"/documents/{doc_id}"))["download_count"]
            download_url = assert_response_ok(client.get(f"/documents/{doc_id}/download"))
            download_count_after = assert_response_ok(client.get(f"/documents/{doc_id}"))["download_count"]
            assert isinstance(download_url, str)
            assert download_count_after == download_count_before + 1
        else:
            download_url = assert_response_ok(client.get(f"/documents/{doc_id}/download"))
            assert isinstance(download_url, str)

    # ------------------------------------------------------------------
    # Success
    # ------------------------------------------------------------------

    def test_owner_can_download_own_public_document(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create(), file_type=".docx")
        self._do_download_success(auth_client, doc.id)

    def test_owner_can_download_own_private_document(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create(), visibility=DocumentVisibility.PRIVATE,  file_type=".docx")
        self._do_download_success(auth_client, doc.id)

    def test_user_can_download_others_public_document(self, auth_client, user, document_factory, category_factory, user_factory):
        other_user = user_factory.create("other_user", "other_user@fakemail", TEST_PASSWORD)
        other_pub_doc = document_factory.create(owner=other_user, category=category_factory.create())

        self._do_download_success(auth_client, other_pub_doc.id)

    def test_user_can_not_download_others_private_document(self, auth_client, user, document_factory, category_factory,
                                                      user_factory):
        other_user = user_factory.create("other_user", "other_user@fakemail", TEST_PASSWORD)
        other_private_doc = document_factory.create(owner=other_user, category=category_factory.create(), visibility=DocumentVisibility.PRIVATE)

        assert_response_error(
            auth_client.get(f"/documents/{other_private_doc.id}/download"),
            ErrorCode.FORBIDDEN,
        )

    def test_guest_can_download_public_document(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create(), file_type=".docx")
        self._do_download_success(client, doc.id, assert_download_count=False)

    def test_guest_can_not_download_private_document(self, client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create(), visibility=DocumentVisibility.PRIVATE, file_type=".docx")
        assert_response_error(
            client.get(f"/documents/{doc.id}/download", params={"format": "./pdf"}),
            ErrorCode.FORBIDDEN,
        )

    def test_document_not_found(self, auth_client):
        assert_response_error(
            auth_client.get("/documents/99999/download"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    @pytest.mark.parametrize("fmt", [".xyz", ".html", ".md", "invalid"])
    def test_unsupported_format(self, auth_client, user, document_factory, category_factory, fmt):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            auth_client.get(f"/documents/{doc.id}/download", params={"format": fmt}),
            ErrorCode.UNSUPPORTED_FILE_TYPE,
        )


class TestSyncDocumentCollections:
    """
    PUT /documents/{document_id}/collections
    """
    @staticmethod
    def _do_sync_success(client, document_id, collection_ids):
        assert_response_ok(
            client.put(f"/documents/{document_id}/collections", json={"collection_ids": collection_ids}),
        )

        # check after sync
        for c_id in collection_ids:
            items = assert_response_ok(client.get(f"/collections/{c_id}/items"))
            assert any(item["id"] == document_id for item in items)
    # ------------------------------------------------------------------
    # Success
    # ------------------------------------------------------------------

    def test_sync_add_document_to_collections(
        self, auth_client, user, document_factory, collection_factory, category_factory
    ):
        doc = document_factory.create(owner=user, category=category_factory.create())
        collections = collection_factory.create_many(n=4, owner=user)

        self._do_sync_success(auth_client, doc.id, [c.id for c in collections])

    def test_sync_remove_document_from_collections(
        self, auth_client, user, document_factory, collection_factory, category_factory
    ):
        doc = document_factory.create(owner=user, category=category_factory.create())
        collections = collection_factory.create_many(n=10, owner=user)

        # add document to all collections
        self._do_sync_success(auth_client, doc.id, [c.id for c in collections])

        # remove document from 1/2 collections
        self._do_sync_success(auth_client, doc.id, [c.id for c in collections[0:5]])


    def test_sync_replaces_existing_collections(
        self, auth_client, user, document_factory, collection_factory, category_factory
    ):
        doc = document_factory.create(owner=user, category=category_factory.create())
        collections = collection_factory.create_many(n=10, owner=user)

        # add document to all collections
        self._do_sync_success(auth_client, doc.id, [c.id for c in collections])

        # replace 1/2 collections by new collections
        new_collections = collections[0:5] + collection_factory.create_many(n=5, owner=user, name_prefix="new_replace")
        self._do_sync_success(auth_client, doc.id, [c.id for c in new_collections[0:5]])


    def test_sync_with_duplicate_collection_ids(
        self, auth_client, user, document_factory, collection_factory, category_factory
    ):
        doc = document_factory.create(owner=user, category=category_factory.create())
        col = collection_factory.create(owner=user)
        self._do_sync_success(auth_client, doc.id, [col.id, col.id])

    # ------------------------------------------------------------------
    # Permission
    # ------------------------------------------------------------------

    def test_unauthenticated(self, client, user, document_factory, collection_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        col = collection_factory.create(owner=user)
        assert_response_error(
            client.put(
                f"/documents/{doc.id}/collections",
                json={"collection_ids": [col.id]},
            ),
            ErrorCode.UNAUTHORIZED,
        )

    def test_cannot_sync_into_others_collection(
        self, auth_client, user, document_factory, collection_factory, category_factory, user_factory
    ):
        other_user = user_factory.create("other_user", "other@mail.com", TEST_PASSWORD)
        doc = document_factory.create(owner=user, category=category_factory.create())
        others_col = collection_factory.create(owner=other_user)
        assert_response_error(
            auth_client.put(
                f"/documents/{doc.id}/collections",
                json={"collection_ids": [others_col.id]},
            ),
            ErrorCode.FORBIDDEN,
        )
    def test_cannot_syn_others_private_document(self, auth_client, user, document_factory, collection_factory, category_factory, user_factory):
        category = category_factory.create()
        own_collections = collection_factory.create_many(n=2, owner=user)
        other_user = user_factory.create("other_user", "other_user@fakemail", TEST_PASSWORD)
        other_private_document = document_factory.create(owner=other_user, visibility=DocumentVisibility.PRIVATE, category=category)

        assert_response_error(
            auth_client.put(f"/documents/{other_private_document.id}/collections", json={"collection_ids": [c.id for c in own_collections]}),
            ErrorCode.FORBIDDEN,
        )
    # ------------------------------------------------------------------
    # Not found
    # ------------------------------------------------------------------

    def test_document_not_found(self, auth_client, user, collection_factory):
        col = collection_factory.create(owner=user)
        assert_response_error(
            auth_client.put(
                "/documents/99999/collections",
                json={"collection_ids": [col.id]},
            ),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_collection_not_found(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            auth_client.put(
                f"/documents/{doc.id}/collections",
                json={"collection_ids": [99999]},
            ),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_partial_collection_not_found(
        self, auth_client, user, document_factory, collection_factory, category_factory
    ):
        doc = document_factory.create(owner=user, category=category_factory.create())
        collections = collection_factory.create_many(n=10, owner=user)

        collection_ids = [c.id for c in collections]
        collection_ids.append(collections[-1].id + 5)
        assert_response_error(
            auth_client.put(
                f"/documents/{doc.id}/collections",
                json={"collection_ids": collection_ids},
            ),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_missing_collection_ids_field(self, auth_client, user, document_factory, category_factory):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            auth_client.put(f"/documents/{doc.id}/collections", json={}),
            ErrorCode.VALIDATION_ERROR,
        )


