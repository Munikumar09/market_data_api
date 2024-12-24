from datetime import date, datetime, timedelta
from time import sleep

import bcrypt
import pytest
from fastapi import HTTPException, status

from app.routers.authentication.authenticate import (
    UserSignupError,
    access_token_from_refresh_token,
    create_token,
    decode_token,
    generate_verification_code,
    get_current_user,
    get_hash_password,
    signin_user,
    signup_user,
    update_user_verification_status,
    validate_date_of_birth,
    validate_email,
    validate_password,
    validate_phone_number,
    verify_password,
)
from app.utils.constants import JWT_REFRESH_SECRET, JWT_SECRET


@pytest.fixture
def mock_session(mocker):
    session = mocker.patch(
        "app.data_layer.database.crud.postgresql.user_crud.get_session"
    )
    session.return_value = session
    session.__enter__.side_effect = session
    session.exec.return_value = session
    return session


def test_validate_email():
    assert validate_email("test@gmail.com") is None

    with pytest.raises(HTTPException):
        validate_email("test@yahoo.com")

    with pytest.raises(HTTPException):
        validate_email("test.com")

    with pytest.raises(HTTPException):
        validate_email("testgmail.com")


def test_validate_phone_number():
    assert validate_phone_number("1234567890") is None

    with pytest.raises(HTTPException):
        validate_phone_number("12345")

    with pytest.raises(HTTPException):
        validate_phone_number("123-456-8901")


def test_get_hash_password():
    password = "Password1!"
    hashed_password = get_hash_password(password)

    assert bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def test_verify_password():
    password = "Password1!"
    hashed_password = get_hash_password(password)

    assert verify_password(password, hashed_password) is None

    with pytest.raises(HTTPException):
        verify_password("wrongpassword", hashed_password)


def test_validate_password():
    assert validate_password("Password1!") is None

    with pytest.raises(HTTPException):
        validate_password("password")

    with pytest.raises(HTTPException):
        validate_password("Paswor@")

    with pytest.raises(HTTPException):
        validate_password("password1")


def test_validate_date_of_birth():
    assert validate_date_of_birth("01/01/2000") is None

    with pytest.raises(HTTPException) as exc:
        validate_date_of_birth((date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))
    assert exc.value.detail == "Date of birth cannot be in the future"

    with pytest.raises(HTTPException) as exc:
        validate_date_of_birth("01-01-2000")
    assert (
        exc.value.detail
        == "Invalid date format for date of birth. Expected format: dd/mm/yyyy"
    )


def test_create_token(token_data):
    token = create_token(token_data, JWT_SECRET, 15)
    decoded_data = decode_token(token, JWT_SECRET)
    assert decoded_data["user_id"] == token_data["user_id"]
    assert decoded_data["email"] == token_data["email"]


def test_access_token_from_refresh_token(token_data):
    refresh_token = create_token(token_data, JWT_REFRESH_SECRET, 15)
    tokens = access_token_from_refresh_token(refresh_token)
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_signup_user(mock_session, mock_user_sign_up_data):
    mock_session.first.side_effect = [None, None, mock_user_sign_up_data]
    response = signup_user(mock_user_sign_up_data)

    assert (
        response["message"]
        == "User created successfully. Please verify your email to activate your account"
    )

    mock_session.first.side_effect = mock_user_sign_up_data
    with pytest.raises(UserSignupError) as signup_error:
        signup_user(mock_user_sign_up_data)

    assert signup_error.value.detail == "email already exists"


def test_signin_user(mock_session, mock_user, mock_user_sign_up_data):
    # User Not found
    mock_session.first.return_value = None
    with pytest.raises(HTTPException) as http_exe:
        signin_user(mock_user_sign_up_data.email, mock_user_sign_up_data.password)
    assert http_exe.value.status_code == status.HTTP_404_NOT_FOUND
    assert http_exe.value.detail == "User not found"

    # invalid password
    mock_session.first.return_value = mock_user
    with pytest.raises(HTTPException) as http_exe:
        signin_user(mock_user_sign_up_data.email, "test_password")

    assert http_exe.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert http_exe.value.detail == "Passwords do not match"

    # user not verified

    with pytest.raises(HTTPException) as http_exe:
        signin_user(mock_user_sign_up_data.email, mock_user_sign_up_data.password)

    assert http_exe.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert http_exe.value.detail == "User is not verified"

    # Successful user login
    mock_user.is_verified = True

    response = signin_user(
        mock_user_sign_up_data.email, mock_user_sign_up_data.password
    )
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

    code = generate_verification_code(10)
    assert len(code) == 10
    assert code.isdigit()


def test_get_current_user(mock_session, token_data, mock_user):
    token = create_token(token_data, JWT_SECRET, 15)
    mock_session.first.return_value = mock_user
    user = get_current_user(token)
    assert user.model_dump() == mock_user.model_dump()


def test_decode_token(token_data):
    token = create_token(token_data, JWT_SECRET, 0.05)

    decoded_data = decode_token(token, JWT_SECRET)
    assert decoded_data["user_id"] == token_data["user_id"]
    assert decoded_data["email"] == token_data["email"]

    sleep(5)
    with pytest.raises(HTTPException) as exc:
        decode_token(token, JWT_SECRET)
    assert exc.value.detail == "Token has expired"

    with pytest.raises(HTTPException) as exc:
        decode_token("invalid_token", JWT_SECRET)
    assert exc.value.detail == "Invalid token"
