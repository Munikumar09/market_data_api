from datetime import datetime, timedelta

from app.data_layer.database.crud.crud_utils import (
    get_data_by_any_condition,
    insert_data,
)
from app.data_layer.database.db_connections.postgresql import (
    create_db_and_tables,
    get_session,
)
from app.data_layer.database.models import DataProvider, Exchange, Instrument
from app.utils.common.types.financial_types import DataProviderType, ExchangeType
from app.utils.token_data import get_token_data

REFRESH_TIME = datetime.strptime("20:30:00", "%H:%M:%S").time()


def is_update_required(dataprovider_type: DataProviderType) -> bool:
    """
    Checks if the data provider data needs to be updated or not with the following conditions:
    1. If the data provider data is not present in the database, then update is required
    2. If the data provider data was last updated more than a day ago, then update is required
    3. If the last update happened after 8:30 AM today, it skips updating
    4. If the last update was more than 1 day ago, it forces an update
    5. If the current time is before 8:30 AM, it prevents premature updates

    Parameters
    ----------
    dataprovider_type: ``DataProviderType``
        The data provider type

    Returns
    -------
    ``bool``
        True if the data provider data needs to be updated, False otherwise
    """

    provider_data = get_data_by_any_condition(
        DataProvider, session=None, id=dataprovider_type.value
    )
    if not provider_data:
        return True

    last_update = provider_data[0].to_dict()["last_updated"]
    current_time = datetime.now()

    if (current_time - last_update) > timedelta(days=1):
        return True

    today_8_30 = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
    if last_update >= today_8_30 or current_time < today_8_30:
        return False

    return True


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
    for provider in DataProviderType:
        if is_update_required(provider):
            processed_data = get_token_data(provider)
            with get_session() as session:
                insert_data(
                    Instrument,
                    processed_data,
                    session=session,
                    update_existing=remove_existing,
                )
        else:
            print(
                f"Skipping update for {provider.name} as it was updated today after 8:30 AM."
            )
