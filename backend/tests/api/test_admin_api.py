from app.core import ErrorCode
from app.models import Category
from tests.utils.api_assertions import assert_response_error, assert_response_ok
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


def test_add_category_success(admin_client):
    assert_response_ok(
        admin_client.post("/admin/categories", json={"name": "NewCreated"})
    )


def test_add_category_failed_duplicate_name(admin_client, seeded_db):
    exists_category = seeded_db.categories[0]
    assert_response_error(
        admin_client.post("/admin/categories", json={"name": exists_category.name}),
        expected_error=ErrorCode.RESOURCE_ALREADY_EXISTS,
    )


def test_rename_category_success(admin_client, seeded_db):
    category = seeded_db.categories[0]
    assert_response_ok(
        admin_client.patch(
            f"/admin/categories/{category.id}", json={"new_name": "NewCategoryName"}
        )
    )


def test_rename_category_failed_duplicate_name(admin_client, seeded_db):
    category_0 = seeded_db.categories[0]
    category_1 = seeded_db.categories[1]
    assert_response_error(
        admin_client.patch(
            f"/admin/categories/{category_0.id}", json={"new_name": category_1.name}
        ),
        expected_error=ErrorCode.RESOURCE_ALREADY_EXISTS,
    )


def test_delete_categories_success(admin_client, seeded_db):
    new_category = Category(name="NewCreated")
    db_session = seeded_db.db_session
    db_session.add(new_category)
    db_session.commit()

    assert_response_ok(admin_client.delete(f"/admin/categories/{new_category.id}"))

    db_session.commit()
    category_in_db = (
        db_session.query(Category).filter(Category.name == "NewCreated").one_or_none()
    )
    assert category_in_db is None


def test_delete_categories_failed(admin_client, seeded_db):
    category_in_use = seeded_db.public_document.category
    assert_response_error(
        admin_client.delete(f"/admin/categories/{category_in_use.id}"),
        expected_error=ErrorCode.RESOURCE_IN_USE,
    )


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
