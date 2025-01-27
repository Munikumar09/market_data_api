# pylint: disable=no-value-for-parameter
from pathlib import Path
from typing import cast

import hydra
from fastapi import APIRouter, Depends, HTTPException, status

from app import ROOT_DIR
from app.data_layer.database.crud.user_crud import get_user_by_attr
from app.data_layer.database.models.user_model import User
from app.notification.email.email_provider import EmailProvider
from app.notification.provider import NotificationProvider
from app.schemas.user_model import EmailVerificationRequest, UserSignIn, UserSignup
from app.utils.common import init_from_cfg
from app.utils.common.logger import get_logger
from app.utils.constants import EMAIL

from .authenticate import (
    get_current_user,
    send_and_save_code,
    signin_user,
    signup_user,
    update_user_verification_status,
    validate_verification_code,
)

# Initialize logging
logger = get_logger(Path(__file__).name)

# Load configuration
with hydra.initialize_config_dir(config_dir=f"{ROOT_DIR}/configs", version_base=None):
    notification_provider_cfg = hydra.compose(config_name="user_verification")

email_notification_provider: EmailProvider = cast(
    EmailProvider,
    init_from_cfg(
        notification_provider_cfg.user_verifier, base_class=NotificationProvider
    ),
)
router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup) -> dict:
    """
    This endpoint is used to register a new user in the system.

    Parameters:
    -----------
    - **user**:
        The user details to be registered in the system
    """
    logger.info("Signup attempt for user: %s", user.email)
    return signup_user(user)


@router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(user: UserSignIn) -> dict:
    """
    This endpoint is used to authenticate a user in the system.

    Parameters:
    -----------
    - **user**:
        The user details to be authenticated in the system
    """
    logger.info("Signin attempt for user: %s", user.email)
    return signin_user(user.email, user.password)


@router.post("/send-verification-code", status_code=status.HTTP_200_OK)
async def send_verification_code(email: str) -> dict:
    """
    Send a verification code to the user's email.

    Parameters:
    -----------
    - **email** (str): The email to send the verification code to.

    Returns:
    --------
    - JSON response indicating whether the code was sent successfully.
    """

    logger.info(
        "Sending verification code to %s using %s", email, email_notification_provider
    )

    # Fetch the user by email address
    user = get_user_by_attr(EMAIL, email)

    # Check if the user is already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified.",
        )
    send_and_save_code(email, user.username, email_notification_provider)
    return {"message": f"Verification code sent to {email}. Valid for 10 minutes."}


@router.post("/verify-code", status_code=status.HTTP_200_OK)
async def verify_user(request: EmailVerificationRequest) -> dict:
    """
    Verify the email of the user using the provided verification code.

    Parameters:
    -----------
    - **request**: UserVerificationRequest
        The request object containing the email and the verification code.

    Returns:
    --------
    - JSON response indicating success or failure of the verification.
    """
    logger.info("Verification attempt for %s", request.email)
    validate_verification_code(request.email, request.verification_code)

    # Update verification status
    update_user_verification_status(request.email)

    return {"message": "Email verified successfully"}


@router.get(
    "/protected-endpoint",
    response_model=dict,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
    },
)
def protected_route(current_user: User = Depends(get_current_user)) -> dict:
    """
    Dummy protected route to test the authentication.

    Parameters:
    -----------
    - **current_user** (dict): The current authenticated user.

    Returns:
    --------
    - JSON response indicating the protected route access.
    """
    logger.info("Access to protected route by user: %s", current_user.email)
    return {"message": "This is a protected route", "user": current_user.model_dump()}
