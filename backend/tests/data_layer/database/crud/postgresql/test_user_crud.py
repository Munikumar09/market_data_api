""" 
This script tests the CRUD operations for the User model in the PostgreSQL database.
"""

from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, create_engine

from app.data_layer.database.crud.postgresql.user_crud import (
    create_or_update_user_verification,
    create_user,
    delete_user,
    get_user,
    get_user_by_attr,
    get_user_verification,
    is_attr_data_in_db,
    update_user,
)
from app.data_layer.database.db_connections.postgresql import get_session
from app.data_layer.database.models.user_model import User, UserVerification

#################### Fixtures ####################


@pytest.fixture(scope="module")
def engine():
    """
    Using sqlite in-memory database instead of PostgreSQL for testing.
    Because it is faster and does not require a separate database server.
    Also, the operations are similar to PostgreSQL.
    """
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """
    Fixture to provide a new database session for each test function.
    Ensures each test runs in isolation with a clean database state.
    """
    with get_session(engine) as session:
        yield session


@pytest.fixture
def test_user():
    """
    Fixture to create a test user object.
    Returns a User instance with predefined attributes for testing.
    """
    return User(
        user_id=12356789012,
        username="testuser",
        email="testuser@gmail.com",
        password="password123",
        date_of_birth=date(1990, 1, 1),
        phone_number="1234567890",
        gender="male",
    )


#################### Tests ####################


# Test: 1
def test_create_user(session, test_user):
    """
    Test creating a new user.
    Ensures `create_user` adds a user to the database.
    """
    create_user(test_user, session=session)

    # Test: 1.1 ( Verify the user was added to the database )
    user = get_user(test_user.user_id, session=session)
    assert user.user_id == test_user.user_id

    # Test: 1.2 ( Verify raising exception when user already exists )
    new_user = User(**test_user.dict())
    with pytest.raises(HTTPException):
        create_user(new_user, session=session)


# Test: 2
def test_get_user(session, test_user):
    """
    Test retrieving a user by user_id.
    Confirms that `get_user` fetches the correct user.
    """
    # Test: 2.1 ( Verify the user is present in the database )
    user = get_user(test_user.user_id, session=session)
    assert user.user_id == test_user.user_id

    # Test: 2.2 ( Verify raising exception when user does not exist )
    with pytest.raises(HTTPException) as exc:
        get_user(1234567890, session=session)
    assert exc.value.detail == "User not found"


# Test: 3
def test_is_attr_data_in_db(session):
    """
    Test if attribute data exists in the database.
    Verifies that `is_attr_data_in_db` detects existing attributes.
    """
    # Test: 3.1 ( Verify the email already exists )
    result = is_attr_data_in_db(User, {"email": "testuser@gmail.com"}, session=session)
    assert result == "email already exists"

    # Test: 3.2 ( Verify the email does not exist )
    assert (
        is_attr_data_in_db(User, {"email": "sampleuser@example.com"}, session=session)
        is None
    )


# Test: 4
def test_get_user_by_attr(session):
    """
    Test retrieving a user by attribute.
    Checks that `get_user_by_attr` returns the correct user.
    """
    # Test: 4.1 ( Verify the user is present in the database with the given email )
    user = get_user_by_attr("email", "testuser@gmail.com", session=session)

    assert user.email == "testuser@gmail.com"

    # Test: 4.2 ( Verify raising exception when user does not exist )
    with pytest.raises(HTTPException) as exc:
        get_user_by_attr("email", "sampleuser@example.com", session=session)

    assert exc.value.detail == "User not found"


# Test: 5
def test_update_user(session, test_user):
    """
    Test updating a user's information.
    Verifies that `update_user` modifies the user's data.
    """
    # Test: 5.1 ( Verify the user is updated )
    update_user(test_user.user_id, {"username": "updated_test_user"}, session=session)
    updated_user = get_user(test_user.user_id, session=session)
    assert updated_user.username == "updated_test_user"

    # Test: 5.2 ( Verify raising exception when user does not exist )
    with pytest.raises(HTTPException) as exc:
        update_user(1234567890, {"username": "updated_test_user"}, session=session)
    assert exc.value.detail == "User not found"

    # Test: 5.3 ( Verify raising exception when invalid field is provided )
    with pytest.raises(HTTPException) as exc:
        update_user(
            test_user.user_id, {"user_name": "updated_test_user"}, session=session
        )
    assert exc.value.detail == "Invalid field: user_name"


# Test: 6
def test_delete_user(session, test_user):
    """
    Test deleting a user.
    Checks that `delete_user` removes the user from the database.
    """

    # Test: 6.1 ( Verify the user is deleted )
    user = get_user(test_user.user_id, session=session)
    assert user.user_id == test_user.user_id

    delete_user(test_user.user_id, session=session)

    # Test: 6.2 ( Verify raising exception when user does not exist )
    with pytest.raises(HTTPException) as exc:
        get_user(test_user.user_id, session=session)
    assert exc.value.detail == "User not found"


# Test: 7
def test_create_or_update_user_verification(session):
    """
    Test creating or updating a user verification object.
    Verifies that verification data is correctly added or updated.
    """
    # Test: 7.1 ( Verify the user verification is created )
    user_verification = UserVerification(
        recipient="testuser@gmail.com",
        verification_code="123456",
        expiration_time=datetime.now(timezone.utc).timestamp(),
        reverified_datetime="2023-12-01T12:00:00",
        verification_medium="email",
    )
    create_or_update_user_verification(user_verification, session=session)
    result = get_user_verification("testuser@gmail.com", session=session)
    assert result.model_dumps() == user_verification.model_dumps()

    # Test: 7.2 ( Verify the user verification is updated )
    updated_verification = UserVerification(
        recipient="testuser@gmail.com",
        verification_code="654321",
        expiration_time=datetime.now(timezone.utc).timestamp(),
        reverified_datetime="2024-12-01T12:00:00",
        verification_medium="email",
    )
    create_or_update_user_verification(updated_verification, session=session)
    result = get_user_verification("testuser@gmail.com", session=session)

    assert result.verification_code == "654321"


# Test: 8
def test_get_user_verification(session):
    """
    Test retrieving a user verification object.
    Ensures `get_user_verification` retrieves the correct verification.
    """
    # Test: 8.1 ( Verify the user verification is retrieved )
    result = get_user_verification("testuser@gmail.com", session=session)
    assert result.recipient == "testuser@gmail.com"

    # Test: 8.2 ( Check if the user verification does not exist )
    assert get_user_verification("sampleuser@gmail.com", session=session) is None
