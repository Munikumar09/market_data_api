# pylint: disable=no-value-for-parameter

import random
import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from snowflake import SnowflakeGenerator

from app.data_layer.database.crud.user_crud import (
    create_user,
    get_user,
    get_user_by_attr,
    is_attr_data_in_db,
    update_user,
)
from app.data_layer.database.models.user_model import Gender, User
from app.schemas.user_model import UserSignup
from app.utils.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_HASHING_ALGO,
    JWT_REFRESH_SECRET,
    JWT_SECRET,
    MACHINE_ID,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

USER_ID = "user_id"
EMAIL = "email"

snowflake_generator = SnowflakeGenerator(MACHINE_ID)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/signin")


def get_snowflake_id() -> int:
    """
    Generate a unique snowflake ID using the snowflake algorithm.

    Returns:
    --------
    ``int``
        The unique snowflake ID
    """
    return next(snowflake_generator)


class UserSignupError(HTTPException):
    """
    Exception class for user signup errors. This class is used to raise exceptions
    when there is an error during user signup. This exception raises when there is
    invalid user data.

    Attributes:
    -----------
    message: ``str``
        The error message to be displayed to the user
    """

    def __init__(self, message: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)


def validate_email(email: str):
    """
    This function validates the email format. It allows only email addresses with
    the domain 'gmail.com'

    Parameters:
    -----------
    email: ``str``
        The email address to be validated
    """
    email_regex = r"^[\w\.-]+@gmail\.com$"

    if re.match(email_regex, email) is None:
        raise UserSignupError("Invalid email format")


def validate_phone_number(phone_number: str) -> None:
    """
    This function validates the phone number format. It allows only phone numbers
    with 10 digits.

    Parameters:
    -----------
    phone_number: ``str``
        The phone number to be validated
    """
    phone_number_regex = r"\d{10}$"

    if re.fullmatch(phone_number_regex, phone_number) is None:
        raise UserSignupError("Invalid phone number format")


def get_hash_password(password: str) -> str:
    """
    It hashes the password using bcrypt and returns the hashed password.

    Parameters:
    -----------
    password: ``str``
        The password to be hashed

    Returns:
    --------
    ``str``
        The hashed password
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def validate_password(password: str):
    """
    Validates the password format. The password must be at least 8 characters long
    and include an uppercase letter, lowercase letter, digit, and special character.

    Parameters:
    -----------
    password: ``str``
        The password to be validated
    """

    if not (
        len(password) >= 8
        and re.search(r"[A-Z]", password) is not None
        and re.search(r"[a-z]", password) is not None
        and re.search(r"\d+", password) is not None
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password) is not None
    ):

        raise UserSignupError(
            "Password must be at least 8 characters long and include an uppercase letter, "
            "lowercase letter, digit, and special character",
        )


def verify_password(password: str, hash_password: str) -> None:
    """
    Verifies the password by comparing the hashed password with the password.

    Parameters:
    -----------
    password: ``str``
        The password to be verified
    hash_password: ``str``
        The hashed password to be compared with the password
    """
    if not bcrypt.checkpw(password.encode("utf-8"), hash_password.encode("utf-8")):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Passwords do not match")


def validate_date_of_birth(date_of_birth: str) -> None:
    """
    Validates the date of birth format. The date of birth must be in the format
    'dd/mm/yyyy' and cannot be in the future.

    Parameters:
    -----------
    date_of_birth: ``str``
        The date of birth to be validated
    """
    try:
        dob = datetime.strptime(date_of_birth, "%d/%m/%Y")

        if dob >= datetime.now():
            raise UserSignupError("Date of birth cannot be in the future")

    except ValueError as exc:
        raise UserSignupError(
            "Invalid date format for date of birth. Expected format: dd/mm/yyyy",
        ) from exc


def validate_user_exists(user: UserSignup) -> str | None:
    """
    Checks if the user already exists in the database. It checks the email
    and phone number fields to see if the user already exists.

    Parameters:
    -----------
    user: ``UserSignup``
        The user details to be checked

    Returns:
    --------
    ``str | None``
        An error message if the user already exists, otherwise None
    """
    fields_to_check = {
        "email": user.email,
        "phone_number": user.phone_number,
    }
    response = is_attr_data_in_db(User, fields_to_check)

    return response


def validate_user_data(user: UserSignup) -> None:
    """
    Validates the user data. If any of the user data is invalid, it raises an exception.

    Parameters:
    -----------
    user: ``UserSignup``
        The user details to be validated
    """
    if user.password != user.confirm_password:
        raise UserSignupError("Passwords do not match")

    validate_email(user.email)
    validate_phone_number(user.phone_number)
    validate_password(user.password)
    validate_date_of_birth(user.date_of_birth)


def create_token(data: dict, secret: str, expire_time: float) -> str:
    """
    Creates a JWT token with the given data and expiration time.

    Parameters:
    -----------
    data: ``dict``
        The data to be encoded in the token
    secret: ``str``
        The secret key used to encode the token
    expire_time: ``int``
        The expiration time of the token in minutes

    Returns:
    --------
    ``str``
        The JWT token
    """
    to_encode = data.copy()

    # Using `exp` as token expiry time, if `exp` is present in the payload data then
    # pyJwt will verify the token expiry automatically
    to_encode.update(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=expire_time)}
    )

    return jwt.encode(to_encode, secret, algorithm=JWT_HASHING_ALGO)


def decode_token(token: str, secret: str) -> dict[str, str]:
    """
    Decodes the given token using the secret key and returns the decoded data.
    The decoded data contain the payload used for creating the token.

    Parameters:
    -----------
    token: ``str``
        The token to be decoded
    secret: ``str``
        The secret key used to decode the token

    Returns:
    --------
    ``dict[str, str]``
        The decoded data from the token
    """
    try:
        return jwt.decode(token, secret, algorithms=[JWT_HASHING_ALGO])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc


def access_token_from_refresh_token(refresh_token: str) -> dict[str, str]:
    """
    Create the access token using the refresh token. If the refresh token is invalid
    or expired, it returns an error message. Otherwise, it generates a new access token
    and returns it.

    Parameters:
    -----------
    refresh_token: ``str``
        The refresh token to generate a new access token

    Returns:
    --------
    ``dict[str, str]``
        A dictionary containing the new access token and the refresh token
    """
    decoded_data = decode_token(refresh_token, JWT_REFRESH_SECRET)

    get_user(decoded_data[USER_ID])

    access_token = create_token(
        {USER_ID: decoded_data[USER_ID], EMAIL: decoded_data[EMAIL]},
        JWT_SECRET,
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def signup_user(user: UserSignup):
    """
    Validates the user data and creates a new user in the system if the user does not
    already exist. If the user already exists, it returns an error message.

    Parameters:
    -----------
    user: ``UserSignup``
        The user details to be registered in the system

    Returns:
    --------
    ``dict``
        A message indicating if the user was created successfully or an error message
    """

    # Check whether the user is already exists with the given details
    if reason := validate_user_exists(user):
        raise UserSignupError(reason)

    user_model = User(
        **user.dict(exclude={"password", "date_of_birth", "gender"}),
        password=get_hash_password(user.password),
        user_id=get_snowflake_id(),
        date_of_birth=datetime.strptime(user.date_of_birth, "%d/%m/%Y"),
        gender=Gender.get_gender_enum(
            gender=user.gender, raise_exception=UserSignupError
        ),
    )

    create_user(user_model)

    if not get_user_by_attr(EMAIL, user.email):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User not created successfully. Please try again later",
        )

    return {
        "message": "User created successfully. Please verify your email to activate your account"
    }


def signin_user(email: str, password: str) -> dict[str, str]:
    """
    Sign in the user with the given email and password. If email or password is incorrect,
    or the user is not verified, it raises an error message. Otherwise, it generates an
    access token and a refresh token and returns them to the user.

    Parameters:
    -----------
    email: ``str``
        The email address of the user
    password: ``str``
        The password of the user

    Returns:
    --------
    ``dict[str, str]``
        Dictionary containing the message, access token, and refresh token
    """
    user = get_user_by_attr(EMAIL, email)
    verify_password(password, user.password)

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not verified",
        )

    token_data = {USER_ID: user.user_id, EMAIL: user.email}
    access_token = create_token(
        token_data,
        JWT_SECRET,
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_token(
        token_data,
        JWT_REFRESH_SECRET,
        REFRESH_TOKEN_EXPIRE_DAYS,
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def update_user_verification_status(
    user_email: str, is_verified: bool = True
) -> dict[str, str]:
    """
    Update the user verification status in the database. If the user does not exist,
    it raises an error message. Otherwise, it updates the user verification status
    and returns a success message.

    Parameters:
    -----------
    user_email: ``str``
        The email address of the user
    is_verified: ``bool`` ( default = True )
        The verification status of the user

    Returns:
    --------
    ``dict[str, str]``
        A message indicating if the user was verified successfully or an error message
    """
    user = get_user_by_attr(EMAIL, user_email)
    user.is_verified = is_verified
    update_user(user.user_id, user.model_dump())

    return {"message": "User verified successfully"}


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a random verification code consisting of numbers only with the given length.

    Parameters:
    -----------
    length: ``int``
        The length of the verification code to be generated

    Returns:
    --------
    ``str``
        The generated verification code
    """
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Retrieve the current user from the database using the access token. If the token
    is invalid or expired, it returns an error message. If the token is valid, it
    retrieves the user details from the database and returns the user.

    Parameters:
    -----------
    token: ``str``
        The access token to retrieve the user details

    Returns:
    --------
    ``User``
        The user details retrieved from the database
    """
    decoded_data = decode_token(token, JWT_SECRET)

    return get_user(decoded_data[USER_ID])
