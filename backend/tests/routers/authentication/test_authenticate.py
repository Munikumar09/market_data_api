""" 
Test cases for the authenticate.py module
"""

from datetime import date, timedelta
from time import sleep

import bcrypt
import pytest
from fastapi import HTTPException, status
from pytest_mock import MockFixture, MockType

from app.data_layer.database.models.user_model import User
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
from app.schemas.user_model import UserSignup
from app.utils.constants import JWT_REFRESH_SECRET, JWT_SECRET


@pytest.fixture
def mock_session(mocker: MockFixture) -> MockType:
    """
    Mock the get_session function to simulate a database session
    """
    session = mocker.patch(
        "app.data_layer.database.db_connections.postgresql.get_session"
    )
    session.return_value = session
    session.__enter__.side_effect = session
    session.exec.return_value = session

    return session


# Test: 1
@pytest.mark.parametrize(
    "email,is_valid",
    [
        ("test@gmail.com", True),
        ("test@yahoo.com", False),
        ("invalid.email", False),
        ("test@.com", False),
        ("test@domain", False),
        ("@domain.com", False),
        ("", False),
        ("test@subdomain.domain.com", False),
    ],
)
def test_validate_email(email: str, is_valid: bool):
    """
    Test validate_email function
    """
    if is_valid:
        assert validate_email(email) is None
    else:
        with pytest.raises(HTTPException):
            validate_email(email)


# Test: 2
def test_validate_phone_number():
    """
    Test validate_phone_number function
    """
    # Test: 2.1 ( Valid phone number )
    assert validate_phone_number("1234567890") is None

    # Test: 2.2 ( Invalid phone number with less than 10 digits )
    with pytest.raises(HTTPException):
        validate_phone_number("12345")

    # Test: 2.3 ( Invalid phone number with more than 10 digits )
    with pytest.raises(HTTPException):
        validate_phone_number("12345678901")

    # Test: 2.4 ( Invalid phone number format )
    with pytest.raises(HTTPException):
        validate_phone_number("123-456-8901")

    with pytest.raises(HTTPException):
        validate_phone_number("-123456789a")


# Test: 3
def test_get_hash_password():
    """
    Test get_hash_password function
    """
    password = "Password1!"
    hashed_password = get_hash_password(password)

    assert bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# Test: 4
def test_verify_password():
    """
    Test verify_password function
    """
    password = "Password1!"
    hashed_password = get_hash_password(password)

    # Test: 4.1 ( Valid password )
    assert verify_password(password, hashed_password) is None

    # Test: 4.2 ( Invalid password )
    with pytest.raises(HTTPException):
        verify_password("wrongpassword", hashed_password)


# Test: 5
@pytest.mark.parametrize(
    "password,is_valid",
    [
        ("Password1!", True),  # Test: 5.1 ( Valid password )
        # Test: 5.2 ( Invalid password with no special character )
        ("Password1", False),
        # Test: 5.3 ( Invalid password with no uppercase character )
        ("password1!", False),
        # Test: 5.4 ( Invalid password with no lowercase character )
        ("PASSWORD1!", False),
        # Test: 5.5 ( Invalid password with no number )
        ("Password!", False),
        # Test: 5.6 ( Invalid password with less than 8 characters )
        ("Pasw1r@", False),
        ("", False),  # Test: 5.7 ( Empty password )
    ],
)
def test_validate_password(password: str, is_valid: bool):
    """
    Test validate_password function
    """
    if is_valid:
        assert validate_password(password) is None
    else:
        with pytest.raises(HTTPException):
            validate_password(password)


# Test: 6
def test_validate_date_of_birth():
    """
    Test validate_date_of_birth function
    """
    # Test: 6.1 ( Valid date of birth )
    assert validate_date_of_birth("01/01/2000") is None

    # Test: 6.2 ( Test with future date )
    with pytest.raises(HTTPException) as exc:
        validate_date_of_birth((date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))
    assert exc.value.detail == "Date of birth cannot be in the future"

    # Test: 6.3 ( Test with invalid date format )
    with pytest.raises(HTTPException) as exc:
        validate_date_of_birth("01-01-2000")
    assert (
        exc.value.detail
        == "Invalid date format for date of birth. Expected format: dd/mm/yyyy"
    )


# Test: 7
def test_create_token(token_data: dict[str, str]):
    """
    Test create_token function
    """
    token = create_token(token_data, JWT_SECRET, 15)
    decoded_data = decode_token(token, JWT_SECRET)
    assert decoded_data["user_id"] == token_data["user_id"]
    assert decoded_data["email"] == token_data["email"]


# Test: 8
def test_access_token_from_refresh_token(
    token_data: dict[str, str], mock_session: MockType
):
    """
    Test access_token_from_refresh_token function
    """
    refresh_token = create_token(token_data, JWT_REFRESH_SECRET, 15)
    tokens = access_token_from_refresh_token(refresh_token)
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    dummy_token = create_token(
        {"user_id": -124, "email": "nothing"}, JWT_REFRESH_SECRET, 1000
    )
    mock_session.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        access_token_from_refresh_token(dummy_token)

    assert exc.value.detail == "User not found"


# Test: 9
def test_signup_user(mock_session: MockType, sign_up_data: UserSignup):
    """
    Test signup_user function
    """
    # Test: 9.1 ( Successful user signup )
    mock_session.first.side_effect = [None, None, sign_up_data]
    response = signup_user(sign_up_data)

    assert (
        response["message"]
        == "User created successfully. Please verify your email to activate your account"
    )

    # Test: 9.2 ( User already exists )
    mock_session.first.side_effect = sign_up_data
    with pytest.raises(UserSignupError) as signup_error:
        signup_user(sign_up_data)

    assert signup_error.value.detail == "email already exists"


# Test: 10
def test_signin_user(mock_session: MockType, test_user: User, sign_up_data: UserSignup):
    """
    Test signin_user function
    """
    # Test: 10.1 ( User not found )
    mock_session.first.return_value = None
    with pytest.raises(HTTPException) as http_exe:
        signin_user(sign_up_data.email, sign_up_data.password)
    assert http_exe.value.status_code == status.HTTP_404_NOT_FOUND
    assert http_exe.value.detail == "User not found"

    # Test: 10.2 ( Incorrect password )
    mock_session.first.return_value = test_user
    with pytest.raises(HTTPException) as http_exe:
        signin_user(sign_up_data.email, "test_password")

    assert http_exe.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert http_exe.value.detail == "Passwords do not match"

    # Test: 10.3 ( User not verified )
    with pytest.raises(HTTPException) as http_exe:
        signin_user(sign_up_data.email, sign_up_data.password)

    assert http_exe.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert http_exe.value.detail == "User is not verified"

    # Test: 10.4 ( Successful user signin )
    test_user.is_verified = True

    response = signin_user(sign_up_data.email, sign_up_data.password)
    assert response.keys() == {"message", "access_token", "refresh_token"}
    assert response["message"] == "Login successful"


# Test: 11
def test_update_user_verification_status(mock_session: MockType, test_user: User):
    """
    Test update_user_verification_status function
    """
    # Test: 11.1 ( User not found )
    mock_session.first.return_value = None

    with pytest.raises(HTTPException) as http_exe:
        update_user_verification_status(test_user.email)

    assert http_exe.value.status_code == status.HTTP_404_NOT_FOUND
    assert http_exe.value.detail == "User not found"
    assert test_user.is_verified is False

    # Test: 11.2 ( Verify user )
    mock_session.first.return_value = test_user
    response = update_user_verification_status(user_email=test_user.email)
    assert response["message"] == "User verified successfully"

    assert test_user.is_verified is True


# Test: 12
def test_generate_verification_code():
    """
    Test generate_verification_code function
    """
    # Test: 12.1 ( Generate verification code of default length 6 )
    code = generate_verification_code()
    assert len(code) == 6
    assert code.isdigit()

    # Test: 12.2 ( Generate verification code of length 10 )
    code = generate_verification_code(10)
    assert len(code) == 10
    assert code.isdigit()


# Test: 13
def test_get_current_user(
    mock_session: MockType, token_data: dict[str, str], test_user: User
):
    """
    Test get_current_user function
    """
    token = create_token(token_data, JWT_SECRET, 15)
    mock_session.first.return_value = test_user
    user = get_current_user(token)
    assert user.model_dump() == test_user.model_dump()


# Test: 14
def test_decode_token(token_data: dict[str, str]):
    """
    Test decode_token function
    """
    # Test: 14.1 ( Valid token )
    token = create_token(token_data, JWT_SECRET, 0.05)

    decoded_data = decode_token(token, JWT_SECRET)
    assert decoded_data["user_id"] == token_data["user_id"]
    assert decoded_data["email"] == token_data["email"]

    # Test: 14.2 ( Expired token )
    sleep(5)
    with pytest.raises(HTTPException) as exc:
        decode_token(token, JWT_SECRET)
    assert exc.value.detail == "Token has expired"

    # Test: 14.3 ( Invalid token )
    with pytest.raises(HTTPException) as exc:
        decode_token("invalid_token", JWT_SECRET)
    assert exc.value.detail == "Invalid token"
