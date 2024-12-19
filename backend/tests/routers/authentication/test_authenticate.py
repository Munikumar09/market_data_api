import pytest

from datetime import datetime
from fastapi import HTTPException, status
from app.routers.authentication.authenticate import (
    validate_email,
    validate_phone_number,
    get_hash_password,
    verify_password,
    validate_password,
    validate_gender,
    validate_date_of_birth,
    create_access_token,
    create_refresh_token,
    decode_token,
    access_token_from_refresh_token,
    signup_user,
    signin_user,
    update_user_verification_status,
    generate_verification_code,
    get_current_user,
    UserSignupError,
)
import bcrypt
from app.schemas.user_model import UserSignup
from app.data_layer.database.models.user_model import User
from app.utils.constants import (
    JWT_REFRESH_SECRET,
    JWT_SECRET,
)


# Mock data
user_data = UserSignup(
    username="testuser",
    email="test@gmail.com",
    phone_number="1234567890",
    password="Password1!",
    confirm_password="Password1!",
    gender="male",
    date_of_birth="01/01/2000",
)


# Mock user model
@pytest.fixture
def mock_user():
    return User(
        user_id=12345678901,
        username=user_data.username,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password=get_hash_password("Password1!"),
        date_of_birth=datetime.strptime(user_data.date_of_birth, "%d/%m/%Y"),
        gender=user_data.gender,
    )


@pytest.fixture
def token_data(mock_user):
    return {"user_id": mock_user.user_id, "email": mock_user.email}


@pytest.fixture
def mock_session(mocker):
    session = mocker.patch(
        "app.data_layer.database.crud.postgresql.user_crud.get_session"
    )
    session.return_value = session
    session.__next__.return_value = session
    session.exec.return_value = session
    return session


def test_validate_email():
    assert validate_email("test@gmail.com")

    with pytest.raises(HTTPException):
        validate_email("test@yahoo.com")


def test_validate_phone_number():
    assert validate_phone_number("1234567890")

    with pytest.raises(HTTPException):
        validate_phone_number("12345")


def test_get_hash_password():
    password = "Password1!"
    hashed_password = get_hash_password(password)

    assert bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def test_verify_password():
    password = "Password1!"
    hashed_password = get_hash_password(password)

    assert verify_password(password, hashed_password)

    with pytest.raises(HTTPException):
        verify_password("wrongpassword", hashed_password)


def test_validate_password():
    assert validate_password("Password1!")

    with pytest.raises(HTTPException):
        validate_password("password")


def test_validate_gender():
    assert validate_gender("male")
    with pytest.raises(HTTPException):
        validate_gender("none")


def test_validate_date_of_birth():
    assert validate_date_of_birth("01/01/2000") == datetime.strptime(
        "01/01/2000", "%d/%m/%Y"
    )
    with pytest.raises(HTTPException):
        validate_date_of_birth("01-01-2000")


def test_create_access_token(token_data):
    token = create_access_token(token_data)
    decoded_data = decode_token(token, JWT_SECRET)
    assert decoded_data["user_id"] == token_data["user_id"]
    assert decoded_data["email"] == token_data["email"]


def test_create_refresh_token(token_data):

    token = create_refresh_token(token_data)
    decoded_data = decode_token(token, JWT_REFRESH_SECRET)
    assert decoded_data["user_id"] == token_data["user_id"]
    assert decoded_data["email"] == token_data["email"]


def test_access_token_from_refresh_token(token_data):
    refresh_token = create_refresh_token(token_data)
    tokens = access_token_from_refresh_token(refresh_token)
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_signup_user(mock_session):

    mock_session.first.side_effect = [None, None, user_data]

    response = signup_user(user_data)
    assert (
        response["message"]
        == "User created successfully. Please verify your email to activate your account"
    )

    mock_session.first.side_effect = user_data
    with pytest.raises(UserSignupError) as signup_error:
        signup_user(user_data)

    assert signup_error.value.detail == {
        "message": "email already exists",
        "status_code": status.HTTP_400_BAD_REQUEST,
    }


def test_signin_user(mock_session, mock_user):
    # User Not found
    mock_session.first.return_value = None
    with pytest.raises(HTTPException) as http_exe:
        signin_user(user_data.email, user_data.password)
    assert http_exe.value.status_code == status.HTTP_404_NOT_FOUND
    assert http_exe.value.detail == "User not found"

    # invalid password
    mock_session.first.return_value = mock_user
    with pytest.raises(HTTPException) as http_exe:
        signin_user(user_data.email, "test_password")

    assert http_exe.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert http_exe.value.detail == "Passwords do not match"

    # user not verified

    with pytest.raises(HTTPException) as http_exe:
        signin_user(user_data.email, user_data.password)

    assert http_exe.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert http_exe.value.detail == "User is not verified"

    # Successful user login
    mock_user.is_verified = True

    response = signin_user(user_data.email, user_data.password)
    assert response.keys() == {"message", "access_token", "refresh_token"}
    assert response["message"] == "Login successful"


def test_update_user_verification_status(mock_session, mock_user):
    mock_session.first.return_value = None
    with pytest.raises(HTTPException) as http_exe:
        update_user_verification_status(mock_user.email)
    assert http_exe.value.status_code == status.HTTP_404_NOT_FOUND
    assert http_exe.value.detail == "User not found"
    assert mock_user.is_verified is False

    mock_session.first.return_value = mock_user
    response = update_user_verification_status(user_email=mock_user.email)
    assert response["message"] == "User verified successfully"

    assert mock_user.is_verified is True


def test_generate_verification_code():
    code = generate_verification_code()
    assert len(code) == 6
    assert code.isdigit()


def test_get_current_user(mock_session, token_data, mock_user):
    token = create_access_token(token_data)
    mock_session.first.return_value = mock_user
    user = get_current_user(token)
    assert user.model_dump() == mock_user.model_dump()
