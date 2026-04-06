from tests.utils.api_assertions import assert_response_ok
from tests.utils.database import admin_client, seeded_db

"""
=====================================================
        USER MANAGEMENT TESTS
=====================================================
"""


def test_list_users(admin_client):
    assert_response_ok(admin_client.get("/admin/users"))


def test_ban_user_success(admin_client, seeded_db):
    user = seeded_db.user
    db_session = seeded_db.db_session

    # make sure user is Active
    user.is_active = True
    db_session.commit()
    db_session.refresh(user)
    assert user.is_active

    assert_response_ok(
        admin_client.post(
            f"/admin/users/{user.id}/ban",
            json={"reason": "Ban reason to notify to user"},
        )
    )

    # check after ban
    db_session.commit()  # commit to start new session and fetch data after update
    db_session.refresh(user)
    print(f"Check after ban: {user.is_active}")
    assert_response_ok(admin_client.get("/admin/users"))
    assert not user.is_active


def test_unban_user_success(admin_client, seeded_db):
    user = seeded_db.user
    db_session = seeded_db.db_session

    # make sure user is not active
    user.is_active = False
    db_session.commit()
    db_session.refresh(user)
    assert not user.is_active

    assert_response_ok(admin_client.post(f"/admin/users/{user.id}/unban"))

    # check after unban
    db_session.commit()  # commit to start new session and fetch data after update
    db_session.refresh(user)
    assert user.is_active


"""
=====================================================
        CATEGORIES MANAGEMENT TESTS
=====================================================
"""


def test_add_category_success(admin_client, seeded_db):
    pass


def test_add_category_failed(admin_client, seeded_db):
    pass


def test_rename_category_success(admin_client, seeded_db):
    pass


def test_rename_category_failed(admin_client, seeded_db):
    pass


def test_delete_categories_success(admin_client, seeded_db):
    pass


def test_delete_categories_failed(admin_client, seeded_db):
    pass


"""
=====================================================
        DOCUMENT REPORTS MANAGEMENT TESTS
=====================================================
"""


def test_list_reported_documents(admin_client, seeded_db):
    pass


def test_list_reports_of_document(admin_client, seeded_db):
    pass


def test_handler_document_reports(admin_client, seeded_db):
    pass


def test_unban_document_success(admin_client, seeded_db):
    pass
