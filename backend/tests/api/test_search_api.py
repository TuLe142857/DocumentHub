from app.core import ErrorCode
from app.models import DocumentVisibility, DocumentStatus, Tag

from tests.utils.api_assertions import assert_response_ok
from tests.utils.category_factory import CategoryFactory
from tests.utils.database import (
    categories,
    category_factory,
    document_factory,
    user_factory,
)
from tests.utils.document_factory import DocumentFactory


class TestSearchDocument:
    def test_search_contain_only_public_documents(
            self,
            client,
            user_factory,
            document_factory: DocumentFactory,
            category_factory: CategoryFactory
    ):
        user = user_factory.create("test_user_pub", "test_user_pub@mail.com", "password")
        category = category_factory.create()
        
        doc_pub = document_factory.create(title="doc1", owner=user, category=category, visibility=DocumentVisibility.PUBLIC, status=DocumentStatus.READY)
        doc_priv = document_factory.create(title="doc2", owner=user, category=category, visibility=DocumentVisibility.PRIVATE, status=DocumentStatus.READY)
        doc_fail = document_factory.create(title="doc3", owner=user, category=category, visibility=DocumentVisibility.PUBLIC, status=DocumentStatus.PROCESSING)

        items = assert_response_ok(client.get("/search"))
        
        doc_ids = [item["id"] for item in items]
        assert doc_pub.id in doc_ids
        assert doc_priv.id not in doc_ids
        assert doc_fail.id not in doc_ids

    def test_search_by_query_q(self, client, user_factory, document_factory, category_factory):
        user = user_factory.create("test_user_q", "q@mail.com", "password")
        category = category_factory.create()
        
        doc1 = document_factory.create(owner=user, category=category, title="Machine Learning Guide")
        doc2 = document_factory.create(owner=user, category=category, title="Deep Learning Book")
        
        items = assert_response_ok(client.get("/search", params={"q": "Machine"}))
        
        doc_ids = [item["id"] for item in items]
        assert doc1.id in doc_ids
        assert doc2.id not in doc_ids

    def test_search_by_types(self, client, user_factory, document_factory, category_factory):
        user = user_factory.create("test_user_types", "types@mail.com", "password")
        category = category_factory.create()
        
        doc_pdf = document_factory.create(title="doc1", owner=user, category=category, file_type=".pdf")
        doc_docx = document_factory.create(title="doc2", owner=user, category=category, file_type=".docx")
        
        items = assert_response_ok(client.get("/search", params={"types": [".pdf"]}))
        
        
        doc_ids = [item["id"] for item in items]
        assert doc_pdf.id in doc_ids
        assert doc_docx.id not in doc_ids

    def test_search_by_category_ids(self, client, user_factory, document_factory, category_factory):
        user = user_factory.create("test_user_cat", "cat@mail.com", "password")
        cat1 = category_factory.create("category_1")
        cat2 = category_factory.create("category_2")
        
        doc1 = document_factory.create(title="doc1", owner=user, category=cat1)
        doc2 = document_factory.create(title="doc2", owner=user, category=cat2)
        
        items = assert_response_ok(client.get("/search", params={"category_ids": [cat1.id]}))

        doc_ids = [item["id"] for item in items]
        assert doc1.id in doc_ids
        assert doc2.id not in doc_ids

    def test_search_by_tags(self, db_session, client, user_factory, document_factory, category_factory):
        user = user_factory.create("test_user_tags", "tags@mail.com", "password")
        category = category_factory.create()
        
        doc_ai = document_factory.create(title="doc_ai", owner=user, category=category)
        tag_ai = Tag.get_or_create("ai", db_session)
        doc_ai.tags.append(tag_ai)
        
        doc_web = document_factory.create(title="doc_web", owner=user, category=category)
        tag_web = Tag.get_or_create("web", db_session)
        doc_web.tags.append(tag_web)
        
        db_session.commit()
        
        items = assert_response_ok(client.get("/search", params={"tags": ["ai"]}))

        
        doc_ids = [item["id"] for item in items]
        assert doc_ai.id in doc_ids
        assert doc_web.id not in doc_ids

    def test_search_combined_filters(self, db_session, client, user_factory, document_factory, category_factory):
        user = user_factory.create("test_user_combined", "combined@mail.com", "password")
        cat1 = category_factory.create("category_1")
        cat2 = category_factory.create("category_2")
        
        tag_ai = Tag.get_or_create("ai", db_session)
        tag_ml = Tag.get_or_create("ml", db_session)
        
        doc1 = document_factory.create(owner=user, category=cat1, title="AI in Healthcare 1", file_type=".pdf")
        doc1.tags.append(tag_ai)
        
        doc2 = document_factory.create(owner=user, category=cat1, title="AI in Finance 1", file_type=".docx")
        doc2.tags.append(tag_ai)
        
        doc3 = document_factory.create(owner=user, category=cat2, title="AI in Healthcare 2", file_type=".pdf")
        doc3.tags.append(tag_ai)
        
        doc4 = document_factory.create(owner=user, category=cat1, title="AI in Healthcare 3", file_type=".pdf")
        doc4.tags.append(tag_ml)
        
        db_session.commit()
        
        params = {
            "q": "Healthcare",
            "category_ids": [cat1.id],
            "types": [".pdf"],
            "tags": ["ai"]
        }
        items = assert_response_ok(client.get("/search", params=params))

        
        doc_ids = [item["id"] for item in items]
        assert doc1.id in doc_ids

        # doc2 keyword not match
        assert doc2.id not in doc_ids

        # doc3 category not match
        assert doc3.id not in doc_ids

        # doc4 tag not match
        assert doc4.id not in doc_ids
