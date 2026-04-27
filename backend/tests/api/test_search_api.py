from app.core import ErrorCode
from app.models import *

from tests.utils.api_assertions import assert_response_ok
from tests.utils.database import categories, category_factory, document_factory, user_factory


class TestSearchDocument:
    def test_success(self, client):
        pass

    def test_search_contain_only_public_documents(self):
        pass



