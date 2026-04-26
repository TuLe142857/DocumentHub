from tests.utils.api_assertions import assert_response_ok
from tests.utils.database import categories


class TestGetCategories:
    def test_success(self, client, categories):
        res_data = assert_response_ok(client.get("/categories"))
        assert isinstance(res_data, list)
        assert all(("id" in category and "name" in category) for category in res_data)
