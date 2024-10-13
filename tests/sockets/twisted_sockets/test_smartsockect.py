# pylint: disable=protected-access
import json
import struct
from itertools import islice
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.sockets.twisted_sockets import SmartSocket
from app.utils.smartapi.smartsocket_types import (
    ExchangeType,
    SubscriptionAction,
    SubscriptionMode,
)


####################### Fixtures #######################
@pytest.fixture
def mock_connection(mocker: MockerFixture):
    """
    Fixture to create a mock SmartApiConnection instance.
    """
    mock_connection = mocker.patch(
        "app.sockets.twisted_sockets.smartsocket.SmartApiConnection",
        autospec=True,
    )

    return mock_connection


@pytest.fixture
def mock_market_data_twisted_socket(mocker: MockerFixture):
    """
    Fixture to create a mock MarketDataTwistedSocket instance.
    """
    return mocker.patch(
        "app.sockets.twisted_sockets.smartsocket.MarketDataTwistedSocket", autospec=True
    )


@pytest.fixture
def mock_logger(mocker: MockerFixture):
    """
    Fixture to create a mock logger instance.
    """
    return mocker.patch("app.sockets.twisted_sockets.smartsocket.logger", autospec=True)


@pytest.fixture
def binary_data_io():
    return (
        b"\x03\x0117758\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00jL\x00\x00\x00\x00\x00\x00\r\x92T~\x92\x01\x00\x00\x1e\xc3\x00\x00\x00"
        + b"\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\n\xc2\x00\x00\x00\x00\x00\x00\xe2\r\x08"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00^\xa6@G\xc2"
        + b"\x00\x00\x00\x00\x00\x00D\xc5\x00\x00\x00\x00\x00\x00Z\xbe\x00\x00\x00\x00\x00\x00"
        + b"\xa1\xc2\x00\x00\x00\x00\x00\x00\x14\xfe\x08g\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00/\x0b\x00\x00\x00\x00\x00\x00\x1e\xc3\x00\x00\x00\x00"
        + b"\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$"
        + b"\xea\x00\x00\x00\x00\x00\x00\x18\x9c\x00\x00\x00\x00\x00\x00v\xca\x00\x00\x00\x00\x00"
        + b"\x00iF\x00\x00\x00\x00\x00\x00",
        {
            "subscription_mode": 3,
            "exchange_type": 1,
            "token": "17758",
            "sequence_number": 19562,
            "exchange_timestamp": 1728696324621,
            "last_traded_price": 49950,
            "subscription_mode_val": "SNAP_QUOTE",
            "last_traded_quantity": 10,
            "average_traded_price": 49674,
            "volume_trade_for_the_day": 527842,
            "total_buy_quantity": 0.0,
            "total_sell_quantity": 2863.0,
            "open_price_of_the_day": 49735,
            "high_price_of_the_day": 50500,
            "low_price_of_the_day": 48730,
            "closed_price": 49825,
            "last_traded_timestamp": 1728642580,
            "open_interest": 0,
            "open_interest_change_percentage": 0,
        },
    )


def get_smartsocket():
    """
    Fixture to create a SmartSocket instance for use in tests.
    """
    auth_token = "auth_token"
    api_key = "api_key"
    client_code = "client_code"
    feed_token = "feed_token"
    correlation_id = "correlation_id"
    subscription_mode = SubscriptionMode.QUOTE
    callback = MagicMock()
    debug = False

    return SmartSocket(
        auth_token=auth_token,
        api_key=api_key,
        client_code=client_code,
        feed_token=feed_token,
        correlation_id=correlation_id,
        subscription_mode=subscription_mode,
        on_data_save_callback=callback,
        debug=debug,
    )


####################### Tests #######################


def test_initialize_socket(mock_connection):
    """
    Test initializing the SmartSocket with the SmartApiConnection.
    """
    mock_connection_instance = mock_connection.get_connection()
    mock_connection_instance.get_connection.return_value = mock_connection_instance
    mock_connection_instance.get_auth_token.return_value = "mock_auth_token"
    mock_connection_instance.api.getfeedToken.return_value = "mock_feed_token"
    mock_connection_instance.credentials.api_key = "mock_api_key"
    mock_connection_instance.credentials.client_id = "mock_client_id"

    cfg = {
        "subscription_mode": "quote",
        "debug": True,
        "correlation_id": "correlation_id",
    }
    socket = SmartSocket.initialize_socket(cfg, on_save_data_callback=MagicMock())

    assert socket.headers["Authorization"] == "mock_auth_token"
    assert socket.headers["x-api-key"] == "mock_api_key"
    assert socket.headers["x-client-code"] == "mock_client_id"
    assert socket.headers["x-feed-token"] == "mock_feed_token"
    assert socket.correlation_id == "correlation_id"
    assert socket.subscription_mode == SubscriptionMode.QUOTE
    assert socket.on_data_save_callback is not None
    assert socket.debug == True
    assert socket._tokens == []
    assert socket.subscribed_tokens == {}


def test_direct_initialization(mocker, mock_connection):
    """
    Test initializing the SmartSocket with the SmartApiConnection.
    """
    mock_connection_instance = mock_connection.get_connection()
    mock_connection_instance.get_connection.return_value = mock_connection_instance
    mock_connection_instance.get_auth_token.return_value = "mock_auth_token"
    mock_connection_instance.api.getfeedToken.return_value = "mock_feed_token"
    mock_connection_instance.credentials.api_key = "mock_api_key"
    mock_connection_instance.credentials.client_id = "mock_client_id"

    socket = SmartSocket(
        auth_token="mock_auth_token",
        api_key="mock_api_key",
        client_code="mock_client_id",
        feed_token="mock_feed_token",
        correlation_id="correlation_id",
        subscription_mode=SubscriptionMode.QUOTE,
        on_data_save_callback=MagicMock(),
        debug=True,
    )

    assert socket.headers["Authorization"] == "mock_auth_token"
    assert socket.headers["x-api-key"] == "mock_api_key"
    assert socket.headers["x-client-code"] == "mock_client_id"
    assert socket.headers["x-feed-token"] == "mock_feed_token"
    assert socket.correlation_id == "correlation_id"
    assert socket.subscription_mode == SubscriptionMode.QUOTE
    assert socket.on_data_save_callback is not None
    assert socket.debug == True
    assert socket._tokens == []
    assert socket.subscribed_tokens == {}


def test_set_tokens(mock_logger):
    """
    Test setting tokens for subscription.
    """
    smartsocket = get_smartsocket()
    tokens = {}
    smartsocket.set_tokens(tokens)
    mock_logger.error.assert_called_once_with(
        "Invalid token format %s, skipping token", {}
    )
    assert len(smartsocket._tokens) == 0
    assert smartsocket._tokens == []

    smartsocket = get_smartsocket()
    tokens = [{"exchangeType": 1, "tokens": {"token1": "name1", "token2": "name2"}}]
    smartsocket.set_tokens(tokens)

    assert len(smartsocket._tokens) == 1
    assert smartsocket.TOKEN_MAP["token1"] == ("name1", ExchangeType.NSE_CM)
    assert smartsocket.TOKEN_MAP["token2"] == ("name2", ExchangeType.NSE_CM)

    assert smartsocket._tokens == [{"exchangeType": 1, "tokens": ["token1", "token2"]}]

    smartsocket = get_smartsocket()
    tokens = {"exchangeType": 1, "tokens": {"token1": "name1", "token2": "name2"}}
    smartsocket.set_tokens(tokens)
    assert len(smartsocket._tokens) == 1
    assert smartsocket.TOKEN_MAP["token1"] == ("name1", ExchangeType.NSE_CM)
    assert smartsocket.TOKEN_MAP["token2"] == ("name2", ExchangeType.NSE_CM)

    assert smartsocket._tokens == [{"exchangeType": 1, "tokens": ["token1", "token2"]}]

    smartsocket = get_smartsocket()
    tokens = {"exchangeType": 1, "tokens": ["token1", "token2"]}

    with pytest.raises(AttributeError):
        smartsocket.set_tokens(tokens)


def test_subscribe(mocker, mock_logger):
    """
    Test subscribing to tokens.
    """
    mock_ws = mocker.MagicMock()
    mock_ws.sendMessage.side_effect = Exception("Test error")
    smartsocket = get_smartsocket()
    smartsocket.ws = mock_ws

    tokens = [
        {"exchangeType": 1, "tokens": ["token1", "token2"]},
        {"exchangeType": 2, "tokens": ["token3", "token4"]},
    ]

    with pytest.raises(Exception):
        smartsocket.subscribe(tokens)
    mock_logger.error.assert_called_once_with(
        "Error while sending message: %s", mock_ws.sendMessage.side_effect
    )

    mock_ws.sendClose.assert_called_once_with(
        None, "Error while sending message: Test error"
    )
    mock_logger.reset_mock()

    mock_ws = mocker.MagicMock()
    smartsocket = get_smartsocket()
    smartsocket.ws = mock_ws
    tokens = [
        {"exchangeType": 1, "tokens": ["token1", "token2"]},
        {"exchangeType": 2, "tokens": ["token3", "token4"]},
    ]

    assert smartsocket.subscribe(tokens)

    mock_ws.sendMessage.assert_called_once_with(
        json.dumps(
            {
                "correlationID": smartsocket.correlation_id,
                "action": SubscriptionAction.SUBSCRIBE.value,
                "params": {
                    "mode": smartsocket.subscription_mode.value,
                    "tokenList": tokens,
                },
            }
        ).encode("utf-8")
    )
    assert smartsocket.subscribed_tokens == {
        "token1": 1,
        "token2": 1,
        "token3": 2,
        "token4": 2,
    }

    assert smartsocket.subscribe({}) == False
    mock_logger.error.assert_called_once_with("No tokens to subscribe")


def test_unsubscribe(mocker, mock_logger):
    """
    Test unsubscribing from tokens.
    """
    mock_ws = mocker.MagicMock()
    smartsocket = get_smartsocket()
    smartsocket.ws = mock_ws
    tokens = [
        {"exchangeType": 1, "tokens": ["token1", "token2"]},
        {"exchangeType": 2, "tokens": ["token3", "token4"]},
    ]

    assert smartsocket.subscribe(tokens)
    mock_ws.reset_mock()

    mock_ws.sendMessage.side_effect = Exception("Test error")
    smartsocket.ws = mock_ws
    tokens_to_unsubscribe = ["token1", "token2"]

    with pytest.raises(Exception):
        smartsocket.unsubscribe(tokens_to_unsubscribe)

    mock_logger.error.assert_called_once_with(
        "Error while sending message to unsubscribe tokens: %s",
        mock_ws.sendMessage.side_effect,
    )

    mock_ws.sendClose.assert_called_once_with(
        None, "Error while sending message: Test error"
    )
    mock_logger.reset_mock()
    mock_ws.reset_mock()
    assert smartsocket.subscribed_tokens == {
        "token1": 1,
        "token2": 1,
        "token3": 2,
        "token4": 2,
    }

    mock_ws = mocker.MagicMock()
    smartsocket.ws = mock_ws
    smartsocket.unsubscribe(["token1", "token2"])

    tokens_to_unsubscribe = [{"exchangeType": 1, "tokens": ["token1", "token2"]}]
    mock_ws.sendMessage.assert_called_once_with(
        json.dumps(
            {
                "correlationId": smartsocket.correlation_id,
                "action": SubscriptionAction.UNSUBSCRIBE.value,
                "params": {
                    "mode": smartsocket.subscription_mode.value,
                    "exchange": tokens_to_unsubscribe,
                },
            }
        ).encode("utf-8")
    )
    assert smartsocket.subscribed_tokens == {"token3": 2, "token4": 2}

    mock_ws = mocker.MagicMock()
    smartsocket.ws = mock_ws
    smartsocket.subscribed_tokens.update({"token1": 1, "token2": 1})
    smartsocket.unsubscribe(["token1", "token5"])

    tokens_to_unsubscribe = [{"exchangeType": 1, "tokens": ["token1"]}]
    mock_ws.sendMessage.assert_called_once_with(
        json.dumps(
            {
                "correlationId": smartsocket.correlation_id,
                "action": SubscriptionAction.UNSUBSCRIBE.value,
                "params": {
                    "mode": smartsocket.subscription_mode.value,
                    "exchange": tokens_to_unsubscribe,
                },
            }
        ).encode("utf-8")
    )
    assert smartsocket.subscribed_tokens == {"token2": 1, "token3": 2, "token4": 2}
    mock_logger.error.assert_any_call("Tokens not subscribed: %s", ["token5"])
    mock_logger.reset_mock()
    smartsocket.unsubscribe([])
    mock_logger.error.assert_called_once_with("No tokens to unsubscribe")


def test_resubscribe(mocker, mock_logger):
    """
    Test resubscribing to previously subscribed tokens.
    """
    mock_ws = mocker.MagicMock()
    smartsocket = get_smartsocket()
    smartsocket.ws = mock_ws

    assert smartsocket.resubscribe() == False
    mock_logger.error.assert_called_once_with("No tokens to subscribe")

    smartsocket.subscribed_tokens = {
        "token1": 1,
        "token2": 1,
    }
    smartsocket.TOKEN_MAP = {
        "token1": ("name1", 1),
        "token2": ("name2", 1),
    }

    assert smartsocket.resubscribe()

    expected_tokens_list = [{"exchangeType": 1, "tokens": ["token1", "token2"]}]

    mock_ws.sendMessage.assert_called_once_with(
        json.dumps(
            {
                "correlationID": smartsocket.correlation_id,
                "action": SubscriptionAction.SUBSCRIBE.value,
                "params": {
                    "mode": smartsocket.subscription_mode.value,
                    "tokenList": expected_tokens_list,
                },
            }
        ).encode("utf-8")
    )


def test_decode_data(binary_data_io):
    """
    Test binary data decoding and parsing.
    """
    binary_data = binary_data_io[0]
    smartsocket = get_smartsocket()
    result = smartsocket.decode_data(binary_data)
    expected_result = binary_data_io[1]
    assert result == expected_result

    binary_data = b"\x01" + binary_data[1:]
    result = smartsocket.decode_data(binary_data)
    ltp_expected_result = dict(islice(expected_result.items(), 0, 7))
    ltp_expected_result["subscription_mode"] = 1
    ltp_expected_result["subscription_mode_val"] = "LTP"
    assert result == ltp_expected_result

    binary_data = b"\x02" + binary_data[1:]
    result = smartsocket.decode_data(binary_data)
    quote_expected_result = dict(islice(expected_result.items(), 0, 16))
    quote_expected_result["subscription_mode"] = 2
    quote_expected_result["subscription_mode_val"] = "QUOTE"
    assert result == quote_expected_result


def test_on_message_callback(binary_data_io):
    """
    Test the data callback when a WebSocket message is received.
    """
    smartsocket = get_smartsocket()

    smartsocket.TOKEN_MAP = {"17758": ("name", ExchangeType.NSE_CM)}

    smartsocket._on_message(None, binary_data_io[0], is_binary=True)
    exptected_data = binary_data_io[1]
    exptected_data.update(
        {
            "name": "name",
            "socket_name": "smartapi",
            "exchange": "NSE_CM",
        }
    )
    actual_call_args = json.loads(smartsocket.on_data_save_callback.call_args.args[0])
    assert actual_call_args.pop("retrieval_timestamp")

    assert smartsocket.on_data_save_callback.call_count == 1
    assert actual_call_args == exptected_data
    smartsocket.on_data_save_callback.reset_mock()

    smartsocket._on_message(None, json.dumps(binary_data_io[1]), is_binary=False)
    actual_call_args = json.loads(smartsocket.on_data_save_callback.call_args.args[0])
    assert actual_call_args.pop("retrieval_timestamp")

    assert smartsocket.on_data_save_callback.call_count == 1
    assert actual_call_args == exptected_data