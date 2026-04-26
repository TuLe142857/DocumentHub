from tests.utils.api_assertions import assert_response_error, assert_response_ok


class TestGetSelfProfile:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass


class TestUpdateSelfProfile:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_validation_error(self):
        pass


class TestUpdateAvatar:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_validation_error(self):
        pass


class TestGetSelfDocuments:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass


class TestGetSelfCollections:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass


class TestGetLikedDocuments:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass


class TestGetOtherUserProfile:
    def test_success(self):
        pass

    def test_user_not_found(self):
        pass


class TestGetOtherUserDocuments:
    def test_success(self):
        pass

    def test_user_not_found(self):
        pass
