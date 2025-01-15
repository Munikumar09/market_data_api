from typing import Generator

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.data_layer.database.db_connections.sqlite import (
    create_db_and_tables,
    get_session,
)
from app.data_layer.database.models import Instrument, InstrumentPrice


@pytest.fixture(scope="function")
def engine() -> Generator[Engine, None, None]:
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
def session(engine) -> Generator[Session, None, None]:
    """
    Fixture to provide a new database session for each test function.
    Ensures each test runs in isolation with a clean database state.
    """
    with get_session(engine) as session:
        yield session


@pytest.fixture
def sample_instrument_data() -> dict[str, str | int | float]:
    """
    Sample instrument data
    """
    return {
        "token": "1594",
        "symbol": "INFY",
        "name": "Infosys Limited",
        "instrument_type": "EQ",
        "exchange": "NSE",
        "expiry_date": "",
        "strike_price": -1.0,
        "tick_size": 5.0,
        "lot_size": 1,
    }


@pytest.fixture
def sample_instrument(sample_instrument_data) -> Instrument:
    """
    Sample instrument object
    """
    return Instrument(**sample_instrument_data)


@pytest.fixture
def sample_instrument_price_data() -> dict[str, str | None]:
    """
    Sample stock price info dictionary
    """
    return {
        "retrieval_timestamp": "2021-09-30 10:00:00",
        "last_traded_timestamp": "2021-09-30 09:59:59",
        "symbol": "INFY",
        "last_traded_price": "1700.0",
        "last_traded_quantity": "100",
        "average_traded_price": "1700.0",
        "volume_trade_for_the_day": "1000",
        "total_buy_quantity": None,
        "total_sell_quantity": None,
    }


@pytest.fixture
def sample_instrument_price(sample_instrument_price_data) -> InstrumentPrice:
    """
    Sample InstrumentPrice object
    """
    return InstrumentPrice(
        symbol=sample_instrument_price_data["symbol"],
        retrieval_timestamp=sample_instrument_price_data["retrieval_timestamp"],
        last_traded_timestamp=sample_instrument_price_data["last_traded_timestamp"],
        last_traded_price=sample_instrument_price_data["last_traded_price"],
        last_traded_quantity=sample_instrument_price_data["last_traded_quantity"],
        average_traded_price=sample_instrument_price_data["average_traded_price"],
        volume_trade_for_the_day=sample_instrument_price_data[
            "volume_trade_for_the_day"
        ],
        total_buy_quantity="500",
        total_sell_quantity="500",
    )


@pytest.fixture
def create_insert_sample_data(session, sample_instrument, sample_instrument_price):
    """
    Insert sample data into the database
    """
    bse_instrument = Instrument(
        **sample_instrument.model_dump(),
    )
    bse_instrument.exchange = "BSE"
    bse_instrument.token = "1020"

    session.add(bse_instrument)
    session.add(sample_instrument)
    session.add(sample_instrument_price)
    session.commit()
