from app.data_layer.database.crud.crud_utils import insert_data
from app.data_layer.database.db_connections.postgresql import (
    create_db_and_tables,
    get_session,
)
from app.data_layer.database.models import DataProvider, Exchange, Instrument
from app.utils.common.types.financial_types import DataProviderType, ExchangeType
from app.utils.fetch_data import fetch_data
from app.utils.smartapi.data_processor import process_token_data
from app.utils.smartapi.urls import SMARTAPI_TOKENS_URL


def insert_exchange_data():
    """
    Inserts the exchange data into the database.
    """
    exchange_data = [
        Exchange(symbol=exchange.name, id=exchange.value) for exchange in ExchangeType
    ]
    with get_session() as session:
        insert_data(Exchange, exchange_data, session=session)


def insert_data_provider_data():
    """
    Inserts the data provider data into the database.
    """
    data_provider_data = [
        DataProvider(name=provider.name, id=provider.value)
        for provider in DataProviderType
    ]
    with get_session() as session:
        insert_data(DataProvider, data_provider_data, session=session)


def create_smartapi_tokens_db(remove_existing: bool = True):
    """
    Creates the SmartAPI tokens database and tables if they do not exist.
    """
    create_db_and_tables()
    insert_exchange_data()
    insert_data_provider_data()
    tokens_data = fetch_data(SMARTAPI_TOKENS_URL)
    for provider in DataProviderType:
        processed_data = process_token_data(tokens_data, provider)
        with get_session() as session:
            insert_data(
                Instrument,
                processed_data,
                session=session,
                update_existing=remove_existing,
            )
