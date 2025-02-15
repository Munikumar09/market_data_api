from datetime import date, datetime
from enum import Enum
from typing import Optional, Type

from pydantic import EmailStr
from sqlmodel import TIMESTAMP, BigInteger, Column, Field, SQLModel, text


class Gender(str, Enum):
    """
    Gender enumeration class to define the gender of the user in the system.
    """

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

    @classmethod
    def get_gender_enum(
        cls, gender: str, raise_exception: Optional[Type[Exception]] = None
    ) -> Optional["Gender"]:
        """
        Returns the Gender enum for the given gender string

        Parameters:
        -----------
        gender: ``str``
            The gender string to get the corresponding Gender enum
        raise_exception: ``Optional[Type[Exception]]``, ( default = None )
            The exception to raise if gender is not in the Gender enum

        Returns:
        --------
        ``Optional[Gender]``
            If gender is present in the Gender enum returns Gender else None
        """
        try:
            return cls(gender.lower())
        except ValueError as exc:
            if raise_exception:
                raise raise_exception(
                    f"Gender must be in {[g.value for g in Gender]}"
                ) from exc

        return None


class User(SQLModel, table=True):  # type: ignore
    """
    User model to store user details in the database.

    Attributes:
    ----------
    user_id: ``int``
        The unique identifier of the user, generated by the snowflake algorithm.
    username: ``str``
        The full name of the user.
    email: ``EmailStr``
        The email address of the user.
    password: ``str``
        The hashed password of the user.
    date_of_birth: ``datetime``
        The date of birth of the user.
    phone_number: ``str``
        The phone number of the user.
    gender: ``Gender``
        The gender of the user.
    is_verified: ``bool``
        A boolean flag to indicate if the user has been verified.
    updated_at: ``datetime``
        The timestamp when the user record was last updated.
    """

    user_id: int = Field(
        ..., sa_column=Column(BigInteger(), primary_key=True, autoincrement=False)
    )
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(min_length=8)
    date_of_birth: date = Field(...)
    phone_number: str = Field(unique=True, index=True, regex="^[0-9]{10}$")
    gender: Gender = Field(...)
    is_verified: bool = Field(default=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
        ),
    )

    def to_dict(self, include_sensitive_data: bool = False):
        """
        Converts the User model to a dictionary
        """
        data = {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "date_of_birth": self.date_of_birth.strftime("%Y-%m-%d"),
            "phone_number": self.phone_number,
            "gender": self.gender.value,
            "is_verified": self.is_verified,
            "updated_at": self.updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        if include_sensitive_data:
            data["password"] = self.password

        return data


class UserVerification(SQLModel, table=True):  # type: ignore
    """
    UserVerification model to store user verification details in the database.

    Attributes:
    ----------
    email: ``str``
        The email address of the user
    verification_code: ``str``
        The verification code sent to the user
    expiration_time: ``int``
        The expiration time of the verification code in seconds
    verification_datetime: ``datetime``
        The datetime when the user was verified for the first time
    reverified_datetime: ``datetime``
        The reverified datetime, if the user reverified the account during the
        password reset process
    """

    email: str = Field(primary_key=True)
    verification_code: str = Field(max_length=6, min_length=6)
    expiration_time: int
    verification_datetime: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    reverified_datetime: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=True,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
        )
    )

    def to_dict(self, include_sensitive_data: bool = False):
        """
        Converts the UserVerification model to a dictionary
        """
        data = {
            "email": self.email,
            "expiration_time": self.expiration_time,
            "verification_datetime": self.verification_datetime,
            "reverified_datetime": self.reverified_datetime,
        }
        if include_sensitive_data:
            data["verification_code"] = self.verification_code

        return data
