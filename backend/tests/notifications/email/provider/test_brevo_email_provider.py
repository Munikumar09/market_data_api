import pytest
from unittest.mock import patch, MagicMock
from omegaconf import DictConfig
from app.notification.email.providers.brevo import BrevoEmailProvider
from brevo_python.rest import ApiException


invalid_cfg_with_error = [
    (
        DictConfig({"security": {"api_key_name": "BREVO_API_KEY"}}),
        "Brevo sender details are required",
    ),
    (
        DictConfig({"sender": {"name": "SENDER_NAME", "email": "SENDER_EMAIL"}}),
        "brevo_api_key_name is required",
    ),
    (
        DictConfig(
            {
                "sender": {"name": "SENDER_NAME"},
                "security": {"api_key_name": "BREVO_API_KEY"},
            }
        ),
        "Brevo sender details are required",
    ),
    (
        DictConfig(
            {
                "sender": {"email": "SENDER_EMAIL"},
                "security": {"api_key_name": "BREVO_API_KEY"},
            }
        ),
        "Brevo sender details are required",
    ),
    (
        DictConfig(
            {
                "sender": {"name": "INVALID_NAME", "email": "SENDER_EMAIL"},
                "security": {"api_key_name": "BREVO_API_KEY"},
            }
        ),
        "Missing required environment variable: INVALID_NAME",
    ),
]


# Mock environment variables
@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("SENDER_NAME", "Test Sender")
    monkeypatch.setenv("SENDER_EMAIL", "sender@example.com")
    monkeypatch.setenv("BREVO_API_KEY", "test_api_key")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("app.notification.email.providers.brevo.logger")


# Test initialization from environment variables
def test_init_from_env_vars(mock_env_vars):
    provider = BrevoEmailProvider("SENDER_NAME", "SENDER_EMAIL", "BREVO_API_KEY")
    assert provider.sender_name == "Test Sender"
    assert provider.sender_email == "sender@example.com"
    assert provider.configuration.api_key["api-key"] == "test_api_key"


# Test initialization from configuration
def test_init_from_cfg(mock_env_vars):
    cfg = DictConfig(
        {
            "sender": {"name": "SENDER_NAME", "email": "SENDER_EMAIL"},
            "security": {"api_key_name": "BREVO_API_KEY"},
        }
    )
    provider = BrevoEmailProvider.from_cfg(cfg)
    assert provider.sender_name == "Test Sender"
    assert provider.sender_email == "sender@example.com"
    assert provider.configuration.api_key["api-key"] == "test_api_key"


@pytest.mark.parametrize("invalid_config", invalid_cfg_with_error)
def test_init_from_cfg_missing_sender(invalid_config, mock_env_vars):
    cfg, error_msg = invalid_config
    with pytest.raises(ValueError) as e:
        BrevoEmailProvider.from_cfg(cfg)
    assert str(e.value) == error_msg


# Test sending notification successfully
@patch("brevo_python.TransactionalEmailsApi.send_transac_email")
def test_send_notification_success(mock_send_email, mock_env_vars):
    provider = BrevoEmailProvider("SENDER_NAME", "SENDER_EMAIL", "BREVO_API_KEY")
    provider.send_notification("123456", "recipient@example.com", "Recipient Name")
    mock_send_email.assert_called_once()


# Test sending notification with API exception
@patch("brevo_python.TransactionalEmailsApi.send_transac_email")
def test_send_notification_api_exception(mock_send_email, mock_env_vars, mock_logger):
    mock_send_email.side_effect = ApiException("API error")
    provider = BrevoEmailProvider("SENDER_NAME", "SENDER_EMAIL", "BREVO_API_KEY")
    provider.send_notification("123456", "recipient@example.com", "Recipient Name")
    mock_logger.error.assert_called_once_with(
        "Exception when calling TransactionalEmailsApi->send_transac_email: %s\n",
        mock_send_email.side_effect,
    )
