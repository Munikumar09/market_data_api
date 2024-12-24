from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.data_layer.database.models.user_model import UserVerification
from app.routers.authentication.authenticate import create_token
from app.routers.authentication.authentication import router
from app.utils.constants import JWT_REFRESH_SECRET, JWT_SECRET

client = TestClient(router)


@pytest.fixture
def mock_signup_user(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.signup_user",
    )


@pytest.fixture
def mock_update_user_verification_status(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.update_user_verification_status",
    )


@pytest.fixture
def mock_get_user_by_attr(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.get_user_by_attr",
    )


@pytest.fixture
def mock_generate_verification_code(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.generate_verification_code",
    )


@pytest.fixture
def mock_create_or_update_user_verification(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.create_or_update_user_verification",
    )


@pytest.fixture
def mock_signin_user(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.signin_user",
    )


@pytest.fixture
def test_verification_code():
    return "123456"


@pytest.fixture
def mock_get_user(mocker):
    return mocker.patch("app.routers.authentication.authenticate.get_user")


class MockNotificationProvider:
    def __init__(self):
        self.code = None
        self.recipient_email = None
        self.recipient_name = None

    def send_notification(self, code, recipient_email, recipient_name):
        self.code = code
        self.recipient = recipient_email
        self.recipient_name = recipient_name
        return {
            "message": f"Verification code sent to {recipient_email}. Valid for 10 minutes."
        }


@pytest.fixture
def mock_notification_provider(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.notification_provider",
        MockNotificationProvider(),
    )


@pytest.fixture
def mock_get_user_verification(mocker):
    return mocker.patch(
        "app.routers.authentication.authentication.get_user_verification"
    )


def test_signup(test_user, mock_signup_user):
    mock_signup_user.return_value = {
        "message": "User created successfully. Please verify your email to activate your account"
    }
    response = client.post("/authentication/signup", json=test_user)
    assert response.status_code == 201
    assert (
        response.json()["message"]
        == "User created successfully. Please verify your email to activate your account"
    )
    mock_signup_user.assert_called_once_with(test_user)
    mock_signup_user.reset_mock()

    mock_signup_user.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="User not created successfully. Please try again later",
    )
    with pytest.raises(HTTPException) as exc:
        client.post("/authentication/signup", json=test_user)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.value.detail == "User not created successfully. Please try again later"


def test_signin(test_user, mock_signin_user, token_data):
    access_token = create_token(token_data, JWT_SECRET, 15)
    refresh_token = create_token(token_data, JWT_REFRESH_SECRET, 15)
    mock_signin_user.return_value = {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    response = client.post(
        "/authentication/signin",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["message"] == "Login successful"
    mock_signin_user.assert_called_once_with(test_user["email"], test_user["password"])
    mock_signin_user.reset_mock()

    mock_signin_user.side_effect = HTTPException(
        status.HTTP_404_NOT_FOUND, "User not found"
    )
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/signin",
            json={"email": test_user["email"], "password": test_user["password"]},
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found"


def test_send_verification_code(
    mock_user,
    mock_notification_provider,
    mock_get_user_by_attr,
    mock_generate_verification_code,
    mock_create_or_update_user_verification,
):
    mock_get_user_by_attr.return_value = mock_user
    mock_generate_verification_code.return_value = "123456"

    response = client.post(
        "/authentication/send-verification-code",
        params={"email_or_phone": mock_user.email, "verification_medium": "email"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Verification code sent to {mock_user.email}. Valid for 10 minutes."
    }
    mock_get_user_by_attr.assert_called_once_with("email", mock_user.email)
    mock_generate_verification_code.assert_called_once()
    mock_create_or_update_user_verification.assert_called_once()
    assert mock_notification_provider.code == "123456"
    assert mock_notification_provider.recipient == mock_user.email
    assert mock_notification_provider.recipient_name == mock_user.username

    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/send-verification-code",
            params={
                "email_or_phone": mock_user.email,
                "verification_medium": "invalid",
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Invalid verification medium. Use 'email' or 'phone'."

    mock_get_user_by_attr.return_value = None

    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/send-verification-code",
            params={"email_or_phone": mock_user.email, "verification_medium": "email"},
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User does not exist with this email or phone."

    mock_user.is_verified = True
    mock_get_user_by_attr.return_value = mock_user
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/send-verification-code",
            params={"email_or_phone": mock_user.email, "verification_medium": "email"},
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Email or phone is already verified."


def test_verify_code(
    mock_user,
    test_verification_code,
    mock_get_user_verification,
    mock_update_user_verification_status,
):
    user_verification = UserVerification(
        recipient=mock_user.email,
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
            "email_or_phone": mock_user.email,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email or phone verified successfully"
    mock_update_user_verification_status.assert_called_once_with(mock_user.email)

    mock_get_user_verification.return_value = None
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/verify-code",
            json={
                "verification_code": test_verification_code,
                "email_or_phone": mock_user.email,
            },
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User does not exist with this email or phone"

    mock_get_user_verification.return_value = user_verification
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/verify-code",
            json={
                "verification_code": "654321",
                "email_or_phone": mock_user.email,
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Invalid verification code"

    user_verification.expiration_time = datetime.now(timezone.utc).timestamp() - 10
    mock_get_user_verification.return_value = user_verification
    with pytest.raises(HTTPException) as exc:
        client.post(
            "/authentication/verify-code",
            json={
                "verification_code": test_verification_code,
                "email_or_phone": mock_user.email,
            },
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Verification code has expired. Try again"


def test_protected_route(mock_user, token_data, mock_get_user):
    access_token = create_token(token_data, JWT_SECRET, 15)
    mock_get_user.return_value = mock_user

    response = client.get(
        "/authentication/protected-endpoint",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"
    current_user = response.json()["user"]
    assert current_user["email"] == mock_user.email
    assert current_user["username"] == mock_user.username
    assert current_user["phone_number"] == mock_user.phone_number
