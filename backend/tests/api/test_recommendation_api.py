from tests.utils.api_assertions import assert_response_ok
from tests.utils.database import auth_client, seeded_db


def test_recommendation_for_me_api(auth_client, seeded_db):
    assert_response_ok(auth_client.get("/recommendation/for_me"))


def test_recommendation_trending_api(client, seeded_db):
    assert_response_ok(client.get("/recommendation/trending"))


def test_recommendation_similar_api(client, seeded_db):
    doc_id = seeded_db.public_document.id
    assert_response_ok(client.get(f"/recommendation/similar/{doc_id}"))
