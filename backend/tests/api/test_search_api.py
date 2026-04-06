from tests.utils.api_assertions import assert_response_ok
from tests.utils.database import auth_client, seeded_db


def test_search_api(client, seeded_db):
    keyword = seeded_db.public_document.title.split()[0]
    search_params = {
        "page": 1,
        "limit": 10,
        "keywords": keyword,
    }
    assert_response_ok(client.get("/search", params=search_params))
