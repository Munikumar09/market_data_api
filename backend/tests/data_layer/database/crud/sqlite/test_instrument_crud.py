"""" 
This module contains tests for the smartapi_crud.py module in the sqlite/crud directory.
"""

from pathlib import Path

import pytest

from app.data_layer.database.crud.sqlite.instrument_crud import (
    get_smartapi_tokens_by_all_conditions,
    get_smartapi_tokens_by_any_condition,
)
from app.data_layer.database.db_connections.sqlite import (
    get_session,
    sqlite_engine,
    create_db_and_tables,
)
from sqlmodel import create_engine

from app.data_layer.database.models import Instrument, InstrumentPrice
from app.utils.startup_utils import create_smartapi_tokens_db
from app.utils.urls import SQLITE_DB_URL
from unittest.mock import MagicMock


from app.data_layer.database.crud.sqlite.websocket_crud import (
    insert_data,
    insert_or_ignore,
    upsert,
)


#################### FIXTURES ####################


@pytest.fixture(scope="module")
def engine():
    """
    Using sqlite in-memory database instead of PostgreSQL for testing.
    Because it is faster and does not require a separate database server.
    Also, the operations are similar to PostgreSQL.
    """
    engine = create_engine("sqlite:///:memory:")
    create_db_and_tables(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """
    Fixture to provide a new database session for each test function.
    Ensures each test runs in isolation with a clean database state.
    """
    with get_session(engine) as session:
        yield session


@pytest.fixture
def sample_instrument_price_info() -> dict[str, str | None]:
    """
    Sample stock price info dictionary
    """
    return {
        "token": "256265",
        "retrieval_timestamp": "2021-09-30 10:00:00",
        "last_traded_timestamp": "2021-09-30 09:59:59",
        "socket_name": "smartsocket",
        "exchange_timestamp": "2021-09-30 09:59:59",
        "name": "Infosys Limited",
        "last_traded_price": "1700.0",
        "exchange": "NSE",
        "last_traded_quantity": "100",
        "average_traded_price": "1700.0",
        "volume_trade_for_the_day": "1000",
        "total_buy_quantity": None,
        "total_sell_quantity": None,
    }


@pytest.fixture
def sample_instrument_price(sample_instrument_price_info) -> InstrumentPrice:
    """
    Sample InstrumentPrice object
    """
    return InstrumentPrice(
        token=sample_instrument_price_info["token"],
        retrieval_timestamp=sample_instrument_price_info["retrieval_timestamp"],
        last_traded_timestamp=sample_instrument_price_info["last_traded_timestamp"],
        socket_name=sample_instrument_price_info["socket_name"],
        exchange_timestamp=sample_instrument_price_info["exchange_timestamp"],
        name=sample_instrument_price_info["name"],
        last_traded_price=sample_instrument_price_info["last_traded_price"],
        exchange=sample_instrument_price_info["exchange"],
        last_traded_quantity=sample_instrument_price_info["last_traded_quantity"],
        average_traded_price=sample_instrument_price_info["average_traded_price"],
        volume_trade_for_the_day=sample_instrument_price_info[
            "volume_trade_for_the_day"
        ],
        total_buy_quantity="500",
        total_sell_quantity="500",
    )


#################### TESTS ####################

#################### Instrument Crud ####################


def test_get_smartapi_tokens_by_any_and_all_condition():
    """
    Test the get_smartapi_tokens_by_any_condition
    """

    db_file_path = Path(SQLITE_DB_URL.split("sqlite:///")[-1])
    remove_at_end = not db_file_path.exists()

    try:
        create_smartapi_tokens_db(True)

        # Insert test data
        token1 = Instrument(
            token="1594",
            symbol="INFY",
            name="INFY",
            instrument_type="EQ",
            exchange="NSE",
            expiry_date="",
            strike_price=-1.0,
            tick_size=5.0,
            lot_size=1,
        )

        # Test get_smartapi_tokens_by_any_condition with symbol
        result = get_smartapi_tokens_by_any_condition(symbol="INFY")
        for item in result:
            assert "INFY" == item.symbol

        # Test get_smartapi_tokens_by_any_condition with exchange
        result = get_smartapi_tokens_by_any_condition(exchange="NSE")
        for item in result:
            assert "NSE" == item.exchange

        # Test get_smartapi_tokens_by_all_conditions with valid conditions
        result = get_smartapi_tokens_by_all_conditions(
            symbol="INFY", exchange="NSE", instrument_type="EQ"
        )
        assert token1.to_dict() == result[0].to_dict()

        # Test get_smartapi_tokens_by_all_conditions with different symbol and exchange
        result = get_smartapi_tokens_by_all_conditions(symbol="SBI", exchange="BSE")
        for item in result:
            assert "SBI" == item.symbol
            assert "BSE" == item.exchange

        # Test get_smartapi_tokens_by_any_condition with instrument_type
        result = get_smartapi_tokens_by_any_condition(instrument_type="EQ")
        for item in result:
            assert "EQ" == item.instrument_type

        # Test all conditions with invalid instrument_type
        result = get_smartapi_tokens_by_all_conditions(
            symbol="INFY", exchange="NSE", instrument_type="INVALID"
        )
        assert len(result) == 0

    finally:
        sqlite_engine.dispose()

        if remove_at_end:
            db_file_path.unlink()


#################### InstrumentPrice Crud ####################


# Test: 1
def test_insert_data_single_dict(
    mock_session: MagicMock, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test insert_data with a single dict and `update_existing=False`
    """
    insert_data(sample_instrument_price_info, update_existing=False)

    mock_session.exec.assert_called_once()  # Ensure exec was called once
    mock_session.commit.assert_called_once()  # Ensure commit was called


def test_insert_with_session(
    mock_session: MagicMock, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test insert_data with a single dict and `update_existing=False` by passing a session
    """
    mock_session.__next__.return_value = mock_session
    insert_data(
        sample_instrument_price_info, session=mock_session, update_existing=False
    )

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 2
def test_insert_data_single_dict_upsert(
    mock_session: MagicMock, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test insert_data with a single dict and `update_existing=True`
    """
    insert_data(sample_instrument_price_info, update_existing=True)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 3
def test_insert_data_empty_input(mock_session: MagicMock, mocker) -> None:
    """
    Test insert_data with empty input (should log a warning and not perform insert)
    """
    mock_logger = mocker.patch(
        "app.data_layer.database.crud.sqlite.websocket_crud.logger"
    )
    insert_data(None, update_existing=False)

    mock_logger.warning.assert_called_once_with(
        "Provided data is empty. Skipping insertion."
    )  # Ensure warning was logged

    mock_session.exec.assert_not_called()  # Ensure exec was not called
    mock_session.commit.assert_not_called()  # Ensure commit was not called


# Test: 4
def test_insert_data_list_dicts(
    mock_session: MagicMock, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test insert_data with a list of dicts and `update_existing=False`
    """
    insert_data([sample_instrument_price_info], update_existing=False)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 5
def test_insert_data_list_dicts_upsert(
    mock_session: MagicMock, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test insert_data with a list of dicts and `update_existing=True`
    """
    insert_data([sample_instrument_price_info], update_existing=True)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 6
def test_insert_data_with_object_conversion(
    mock_session: MagicMock, sample_instrument_price: InstrumentPrice
) -> None:
    """
    Test insert_data with a InstrumentPrice object
    """
    insert_data(sample_instrument_price, update_existing=False)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 7
def test_upsert(
    mock_session, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test upsert logic
    """

    mock_session.__next__.return_value = mock_session
    upsert(sample_instrument_price_info, session=mock_session)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()


# Test: 8
def test_insert_or_ignore(
    mock_session: MagicMock, sample_instrument_price_info: dict[str, str | None]
) -> None:
    """
    Test insert_or_ignore logic
    """
    mock_session.__next__.return_value = mock_session
    insert_or_ignore(sample_instrument_price_info, session=mock_session)

    mock_session.exec.assert_called_once()
    mock_session.commit.assert_called_once()
