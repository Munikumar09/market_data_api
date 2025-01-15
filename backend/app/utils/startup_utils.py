from app.data_layer.database.crud.crud_utils import insert_data
from app.data_layer.database.db_connections.sqlite import (
    create_db_and_tables,
    get_session,
)
from app.data_layer.database.models import Instrument
from app.utils.fetch_data import fetch_data
from app.utils.smartapi.data_processor import process_token_data
from app.utils.smartapi.urls import SMARTAPI_TOKENS_URL


def create_smartapi_tokens_db(remove_existing: bool = True):
    """
    Creates the SmartAPI tokens database and tables if they do not exist.
    """
    create_db_and_tables()
    tokens_data = fetch_data(SMARTAPI_TOKENS_URL)
    processed_data = process_token_data(tokens_data)
    with get_session() as session:
        insert_data(
            Instrument, processed_data, session=session, update_existing=remove_existing
        )
