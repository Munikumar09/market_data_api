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
    Mock the signup_user function.
    """
    return mocker.patch("app.routers.authentication.authentication.signup_user")


@pytest.fixture
def mock_update_user_verification_status(mocker: MockFixture):
    """
    Mock the update_user_verification_status function.
    """
    return mocker.patch(
        "app.routers.authentication.authentication.update_user_verification_status"
    )


@pytest.fixture
def mock_get_user_by_attr(mocker: MockFixture):
    """
    Mock the get_user_by_attr function.
    """
    return mocker.patch("app.routers.authentication.authentication.get_user_by_attr")


@pytest.fixture
def mock_generate_verification_code(mocker: MockFixture):
    """
    Mock the generate_verification_code function.
    """
    return mocker.patch(
        "app.routers.authentication.authenticate.generate_verification_code"
    )


@pytest.fixture
def mock_create_or_update_user_verification(mocker: MockFixture):
    """
    Mock the create_or_update_user_verification function.
    """
    return mocker.patch(
        "app.routers.authentication.authenticate.create_or_update_user_verification"
    )


@pytest.fixture
def mock_create_or_update_user_verification_authentication(mocker: MockFixture):
    """
    Mock the create_or_update_user_verification function in authentication.
    """
    return mocker.patch(
        "app.routers.authentication.authentication.create_or_update_user_verification"
    )


@pytest.fixture
def mock_signin_user(mocker: MockFixture):
    """
    Mock the signin_user function.
    """
    return mocker.patch("app.routers.authentication.authentication.signin_user")


@pytest.fixture
def mock_get_user(mocker: MockFixture):
    """
    Mock the get_user function.
    """
    return mocker.patch("app.routers.authentication.authenticate.get_user")


@pytest.fixture
def mock_notification_provider(mocker: MockFixture):
    """
    Mock the notification provider.
    """
    return mocker.patch(
        "app.routers.authentication.authentication.email_notification_provider",
        MockNotificationProvider(),
    )


@pytest.fixture
def mock_get_user_verification(mocker: MockFixture):
    """
    Mock the get_user_verification function.
    """
    return mocker.patch("app.routers.authentication.authenticate.get_user_verification")


@pytest.fixture
def mock_validate_verification_code(mocker: MockFixture):
    """
    Mock the validate_verification_code function.
    """
    return mocker.patch(
        "app.routers.authentication.authentication.validate_verification_code",
    )


@pytest.fixture
def mock_authenticate_user(mocker: MockFixture):
    """
    Mock the authenticate_user function.
    """
    return mocker.patch(
        "app.routers.authentication.authentication.authenticate_user",
    )


@pytest.fixture
def mock_update_password(mocker: MockFixture):
    """
    Mock the update_password function.
    """
    return mocker.patch(
        "app.routers.authentication.authentication.update_password",
    )


@pytest.fixture
def mock_update_user(mocker: MockFixture):
    """
    Mock the update_user function.
    """
    return mocker.patch("app.routers.authentication.authenticate.update_user")


@pytest.fixture
def test_verification_code():
    """
    Verification code for testing.
    """
    return "123456"


class MockNotificationProvider:
    """
    This class mocks the notification provider.
    """

    def __init__(self):
        self.code = None
        self.recipient_email = None
        self.recipient_name = None

    def send_notification(self, code: str, recipient_email: str, recipient_name: str):
        """
        Test method to send a notification.
        """
        self.code = code
        self.recipient_email = recipient_email
        self.recipient_name = recipient_name
        return {
            "message": f"Verification code sent to {recipient_email}. Valid for 10 minutes."
        }


#################### TESTS ####################


def test_signup(sign_up_data: UserSignup, mock_signup_user: MockType) -> None:
    """
    Test the signup functionality.
    Verifies that a user can sign up successfully and handles errors appropriately.
    """
    # Successful signup
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

    # Test for the existing user
    mock_signup_user.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{sign_up_data.email} already exists",
    )
    with pytest.raises(HTTPException) as exc:
        client.post("/authentication/signup", json=sign_up_data.dict())

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == f"{sign_up_data.email} already exists"


def test_signin(
    sign_up_data: UserSignup, mock_signin_user: MockType, token_data: dict
) -> None:
    """
    Test the signin functionality.
    Verifies that a user can sign in successfully and handles errors appropriately.
    """
    # Successful signin
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

    # Invalid credentials
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


def test_send_verification_code(
    test_user: User,
    mock_notification_provider: MockNotificationProvider,
    mock_get_user_by_attr: MockType,
    mock_generate_verification_code: MockType,
    mock_create_or_update_user_verification: MockType,
) -> None:
    """
    Test the send verification code functionality.
    Verifies that a verification code is sent to the user and handles errors appropriately.
    """
    # Successful verification code sent
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

    # Email is already verified
    test_user.is_verified = True
    mock_get_user_by_attr.return_value = test_user
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/send-verification-code",
            params={"email": test_user.email},
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Email is already verified."

    # User does not exist
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


def test_verify_code(
    test_user: User,
    test_verification_code: str,
    mock_get_user_verification: MockType,
    mock_update_user_verification_status: MockType,
) -> None:
    """
    Test the verify code functionality.
    Verifies that a verification code can be used to verify a user and handles errors appropriately.
    """
    # Successful verification
    user_verification = UserVerification(
        email=test_user.email,
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

    # User does not exist
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
    assert exc.value.detail == "User does not exist with this email"

    # Invalid verification code
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

    # Verification code has expired
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


def test_protected_route(
    test_user: User, token_data: dict, mock_get_user: MockType
) -> None:
    """
    Test the protected route functionality.
    Verifies that a protected route can be accessed with a valid token and handles errors appropriately.
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


def test_send_reset_password_code(
    test_user: User,
    mock_notification_provider: MockNotificationProvider,
    mock_get_user_by_attr: MockType,
    mock_generate_verification_code: MockType,
    mock_create_or_update_user_verification: MockType,
) -> None:
    """
    Test the send reset password code functionality.
    Verifies that a reset password code is sent to the user and handles errors appropriately.
    """
    # Successful reset password code sent
    mock_get_user_by_attr.return_value = test_user
    mock_generate_verification_code.return_value = "123456"

    response = client.get(
        "/authentication/sent-reset-password-code", params={"email": test_user.email}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Reset password code sent to {test_user.email}. Valid for 10 minutes."
    }
    mock_get_user_by_attr.assert_called_once_with("email", test_user.email)
    mock_generate_verification_code.assert_called_once()
    mock_create_or_update_user_verification.assert_called_once()
    assert mock_notification_provider.code == "123456"
    assert mock_notification_provider.recipient_email == test_user.email
    assert mock_notification_provider.recipient_name == test_user.username

    # User does not exist
    mock_get_user_by_attr.side_effect = HTTPException(
        status.HTTP_404_NOT_FOUND, f"User not found with given email {test_user.email}"
    )
    with pytest.raises(HTTPException) as exc:
        client.get(
            "/authentication/sent-reset-password-code",
            params={"email": test_user.email},
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == f"User not found with given email {test_user.email}"
    mock_get_user_by_attr.reset_mock()


def test_reset_password(
    test_user: User,
    test_verification_code: str,
    mock_get_user_by_attr: MockType,
    mock_validate_verification_code: MockType,
    mock_update_password: MockType,
    mock_create_or_update_user_verification_authentication: MockType,
) -> None:
    """
    Test the reset password functionality.
    Verifies that a user can reset their password using a verification code and handles errors appropriately.
    """
    valid_password = "NewPassword1@"
    # Successful password reset
    mock_validate_verification_code.return_value = UserVerification(
        email=test_user.email,
        verification_medium="email",
        verification_code=test_verification_code,
        expiration_time=int(
            (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
        ),
    )
    mock_get_user_by_attr.return_value = test_user

    response = client.post(
        "/authentication/reset-password",
        json={
            "email": test_user.email,
            "password": valid_password,
            "verification_code": test_verification_code,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully"
    mock_update_password.assert_called_once_with(
        test_user.user_id, test_user.password, valid_password
    )
    mock_create_or_update_user_verification_authentication.assert_called_once()

    # Invalid verification code
    mock_validate_verification_code.side_effect = HTTPException(
        status.HTTP_400_BAD_REQUEST, "Invalid verification code"
    )
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/reset-password",
            json={
                "email": test_user.email,
                "password": "new_password",
                "verification_code": "invalid_code",
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Invalid verification code"
    mock_validate_verification_code.reset_mock(side_effect=True)

    # User does not exist
    mock_get_user_by_attr.side_effect = HTTPException(
        status.HTTP_404_NOT_FOUND, f"User not found with given email {test_user.email}"
    )

    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/reset-password",
            json={
                "email": test_user.email,
                "password": "new_password",
                "verification_code": test_verification_code,
            },
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == f"User not found with given email {test_user.email}"
    mock_get_user_by_attr.reset_mock()


def test_change_password(
    test_user: User,
    sign_up_data: UserSignup,
    mock_authenticate_user: MockType,
    mock_update_user: MockType,  # pylint: disable=unused-argument
) -> None:
    """
    Test the change password functionality.
    Verifies that a user can change their password and handles errors appropriately.
    """
    valid_password = "NewPassword1@"

    # Successful password change
    mock_authenticate_user.return_value = test_user

    response = client.post(
        "/authentication/change-password",
        json={
            "email": test_user.email,
            "old_password": sign_up_data.password,
            "new_password": valid_password,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    # Invalid old password
    mock_authenticate_user.side_effect = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Invalid credentials"
    )
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/change-password",
            json={
                "email": test_user.email,
                "old_password": "invalid_old_password",
                "new_password": valid_password,
            },
        )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid credentials"

    # User does not exist
    mock_authenticate_user.side_effect = HTTPException(
        status.HTTP_404_NOT_FOUND, f"User not found with given email {test_user.email}"
    )
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/change-password",
            json={
                "email": test_user.email,
                "old_password": sign_up_data.password,
                "new_password": valid_password,
            },
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == f"User not found with given email {test_user.email}"
    mock_authenticate_user.reset_mock(side_effect=True)

    # New password is the same as the old password
    mock_authenticate_user.return_value = test_user
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/change-password",
            json={
                "email": test_user.email,
                "old_password": sign_up_data.password,
                "new_password": sign_up_data.password,
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "New password cannot be the same as the old password"
