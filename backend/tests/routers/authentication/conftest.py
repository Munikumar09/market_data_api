from datetime import datetime

import pytest

from app.data_layer.database.models.user_model import User
from app.routers.authentication.authenticate import get_hash_password
from app.schemas.user_model import UserSignup


# Mock data
@pytest.fixture
def mock_user_sign_up_data():
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
def mock_user(mock_user_sign_up_data):
    return User(
        user_id=12345678901,
        username=mock_user_sign_up_data.username,
        email=mock_user_sign_up_data.email,
        phone_number=mock_user_sign_up_data.phone_number,
        password=get_hash_password("Password1!"),
        date_of_birth=datetime.strptime(
            mock_user_sign_up_data.date_of_birth, "%d/%m/%Y"
        ),
        gender=mock_user_sign_up_data.gender,
    )


@pytest.fixture
def token_data(mock_user):
    return {"user_id": mock_user.user_id, "email": mock_user.email}
