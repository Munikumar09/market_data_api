from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pytest_mock import MockFixture, MockType

from app.data_layer.database.models.user_model import User, UserVerification
from app.routers.authentication.authenticate import create_token
from app.routers.authentication.authentication import router
from app.schemas.user_model import UserSignup
from app.utils.constants import JWT_REFRESH_SECRET, JWT_SECRET

client = TestClient(router)


#################### FIXTURES ####################


@pytest.fixture
def mock_signup_user(mocker: MockFixture):
    """
    Mock the signup_user function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.signup_user",
    )


@pytest.fixture
def mock_update_user_verification_status(mocker: MockFixture):
    """
    Mock the update_user_verification_status function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.update_user_verification_status",
    )


@pytest.fixture
def mock_get_user_by_attr(mocker: MockFixture):
    """
    Mock the get_user_by_attr function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.get_user_by_attr",
    )


@pytest.fixture
def mock_generate_verification_code(mocker: MockFixture):
    """
    Mock the generate_verification_code function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.generate_verification_code",
    )


@pytest.fixture
def mock_create_or_update_user_verification(mocker: MockFixture):
    """
    Mock the create_or_update_user_verification function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.create_or_update_user_verification",
    )


@pytest.fixture
def mock_signin_user(mocker: MockFixture):
    """
    Mock the signin_user function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.signin_user",
    )


@pytest.fixture
def mock_get_user(mocker: MockFixture):
    """
    Mock the get_user function
    """
    return mocker.patch("app.routers.authentication.authenticate.get_user")


@pytest.fixture
def mock_notification_provider(mocker: MockFixture):
    """
    Mock the notification provider
    """
    return mocker.patch(
        "app.routers.authentication.authentication.email_notification_provider",
        MockNotificationProvider(),
    )


@pytest.fixture
def mock_get_user_verification(mocker: MockFixture):
    """
    Mock the get_user_verification function
    """
    return mocker.patch(
        "app.routers.authentication.authentication.get_user_verification"
    )


@pytest.fixture
def test_verification_code():
    """
    Verification code for testing
    """
    return "123456"


class MockNotificationProvider:
    """
    This class mocks the notification provider
    """

    def __init__(self):
        self.code = None
        self.recipient_email = None
        self.recipient_name = None

    def send_notification(self, code: str, recipient_email: str, recipient_name: str):
        """
        Test method to send a notification
        """
        self.code = code
        self.recipient_email = recipient_email
        self.recipient_name = recipient_name
        return {
            "message": f"Verification code sent to {recipient_email}. Valid for 10 minutes."
        }


#################### TESTS ####################


# Test: 1
def test_signup(sign_up_data: UserSignup, mock_signup_user: MockType) -> None:
    """
    Test the signup functionality. Verifies that a user can sign up
    successfully and handles errors appropriately.
    """
    # Test: 1.1 ( Successful signup )
    mock_signup_user.return_value = {
        "message": "User created successfully. Please verify your email to activate your account"
    }
    response = client.post("/authentication/signup", json=sign_up_data.dict())

    assert response.status_code == 201
    assert (
        response.json()["message"]
        == "User created successfully. Please verify your email to activate your account"
    )

    mock_signup_user.assert_called_once_with(sign_up_data.dict())
    mock_signup_user.reset_mock()

    # Test: 1.2 ( Test for the existing user )
    mock_signup_user.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{sign_up_data.email} already exists",
    )
    with pytest.raises(HTTPException) as exc:
        client.post("/authentication/signup", json=sign_up_data.dict())

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == f"{sign_up_data.email} already exists"


# Test: 2
def test_signin(
    sign_up_data: UserSignup, mock_signin_user: MockType, token_data: dict
) -> None:
    """
    Test the signin functionality. Verifies that a user can sign in successfully
    and handles errors appropriately.
    """
    # Test: 2.1 ( Successful signin )
    access_token = create_token(token_data, JWT_SECRET, 15)
    refresh_token = create_token(token_data, JWT_REFRESH_SECRET, 15)
    mock_signin_user.return_value = {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    response = client.post(
        "/authentication/signin",
        json={
            "email": sign_up_data.email,
            "password": sign_up_data.password,
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["message"] == "Login successful"
    mock_signin_user.assert_called_once_with(sign_up_data.email, sign_up_data.password)
    mock_signin_user.reset_mock()

    # Test: 2.2 ( Invalid credentials )
    mock_signin_user.side_effect = HTTPException(
        status.HTTP_404_NOT_FOUND, "User not found"
    )
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/signin",
            json={
                "email": sign_up_data.email,
                "password": sign_up_data.password,
            },
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


# Test: 3
def test_send_verification_code(
    test_user: User,
    mock_notification_provider: MockNotificationProvider,
    mock_get_user_by_attr: MockType,
    mock_generate_verification_code: MockType,
    mock_create_or_update_user_verification: MockType,
) -> None:
    """
    Test the send verification code functionality. Verifies that a verification code
    is sent to the user and handles errors appropriately.
    """
    # Test: 3.1 ( Successful verification code sent )
    mock_get_user_by_attr.return_value = test_user
    mock_generate_verification_code.return_value = "123456"

    response = client.post(
        "/authentication/send-verification-code", params={"email": test_user.email}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Verification code sent to {test_user.email}. Valid for 10 minutes."
    }
    mock_get_user_by_attr.assert_called_once_with("email", test_user.email)
    mock_generate_verification_code.assert_called_once()
    mock_create_or_update_user_verification.assert_called_once()
    assert mock_notification_provider.code == "123456"
    assert mock_notification_provider.recipient_email == test_user.email
    assert mock_notification_provider.recipient_name == test_user.username

    # Test: 3.2 ( Email is already verified )
    test_user.is_verified = True
    mock_get_user_by_attr.return_value = test_user
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/send-verification-code",
            params={"email": test_user.email},
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Email is already verified."

    # # Test: 3.3 ( User does not exist )
    mock_get_user_by_attr.side_effect = HTTPException(
        status.HTTP_404_NOT_FOUND, f"User not found with given email {test_user.email}"
    )
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/send-verification-code", params={"email": test_user.email}
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == f"User not found with given email {test_user.email}"
    mock_get_user_by_attr.reset_mock()


# Test: 4
def test_verify_code(
    test_user: UserSignup,
    test_verification_code: str,
    mock_get_user_verification: MockType,
    mock_update_user_verification_status: MockType,
) -> None:
    """
    Test the verify code functionality. Verifies that a verification code can
    be used to verify a user and handles errors appropriately.
    """
    # Test: 4.1 ( Successful verification )
    user_verification = UserVerification(
        recipient=test_user.email,
        verification_medium="email",
        verification_code=test_verification_code,
        expiration_time=int(
            (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
        ),
    )
    mock_get_user_verification.return_value = user_verification
    response = client.post(
        "/authentication/verify-code",
        json={
            "verification_code": test_verification_code,
            "email": test_user.email,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"
    mock_update_user_verification_status.assert_called_once_with(test_user.email)

    # Test: 4.2 ( User does not exist )
    mock_get_user_verification.return_value = None
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/verify-code",
            json={
                "verification_code": test_verification_code,
                "email": test_user.email,
            },
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User does not exist with this email or phone"

    # Test: 4.3 ( Invalid verification code )
    mock_get_user_verification.return_value = user_verification
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/verify-code",
            json={
                "verification_code": "654321",
                "email": test_user.email,
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Invalid verification code"

    # Test: 4.4 ( Verification code has expired )
    user_verification.expiration_time = int(datetime.now(timezone.utc).timestamp() - 10)
    mock_get_user_verification.return_value = user_verification
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/verify-code",
            json={
                "verification_code": test_verification_code,
                "email": test_user.email,
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Verification code has expired. Try again"


# Test: 5
def test_protected_route(
    test_user: UserSignup, token_data: dict, mock_get_user: MockType
) -> None:
    """
    Test the protected route functionality. Verifies that a protected route can
    be accessed with a valid token and handles errors appropriately.
    """
    access_token = create_token(token_data, JWT_SECRET, 15)
    mock_get_user.return_value = test_user

    response = client.get(
        "/authentication/protected-endpoint",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"
    current_user = response.json()["user"]
    assert current_user["email"] == test_user.email
    assert current_user["username"] == test_user.username
    assert current_user["phone_number"] == test_user.phone_number
