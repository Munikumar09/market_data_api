from datetime import datetime

import pytest

from app.data_layer.database.models.user_model import User
from app.routers.authentication.authenticate import get_hash_password
from app.schemas.user_model import UserSignup


# Mock data
@pytest.fixture
def sign_up_data() -> UserSignup:
    return UserSignup(
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
def test_user(sign_up_data: UserSignup) -> User:
    return User(
        user_id=12345678901,
        username=sign_up_data.username,
        email=sign_up_data.email,
        phone_number=sign_up_data.phone_number,
        password=get_hash_password("Password1!"),
        date_of_birth=datetime.strptime(sign_up_data.date_of_birth, "%d/%m/%Y"),
        gender=sign_up_data.gender,
    )


@pytest.fixture
def token_data(test_user) -> dict[str, str]:
    return {"user_id": test_user.user_id, "email": test_user.email}
