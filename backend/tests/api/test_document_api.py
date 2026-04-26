import pytest

from app.models import *
from tests.utils.api_assertions import assert_response_error, assert_response_ok


class TestGetDocumentMeta:
    def test_get_supported_types(self, client):
        pass

    def test_get_max_upload_size(self, client):
        pass


class TestUploadDocument:
    def test_success(self):
        pass


class TestGetDocumentDetails:
    pass


class TestUpdateDocument:
    pass


class TestDeleteDocument:
    pass


class TestRestoreDocument:
    pass


class TestDocumentTags:
    pass


class TestDocumentLike:
    pass


class TestDownloadDocument:
    pass


class TestSyncDocumentCollections:
    pass
