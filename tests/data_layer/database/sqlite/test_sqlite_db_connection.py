""" 
Test the database connection and interaction with the SQLite database.
"""

from pathlib import Path

from sqlmodel import inspect, select

from app.data_layer.database.sqlite.models.smartapi_models import SmartAPIToken
from app.data_layer.database.sqlite.sqlite_db_connection import (
    create_db_and_tables,
    get_session,
    sqlite_engine,
)
from app.utils.urls import SQLITE_DB_URL

table_names = ["smartapitoken", "socketstockpriceinfo"]


def test_database_init_and_interaction():
    """
    Test if the database is created and tables are created and empty and able to interact with the database.
    """

    db_file_path = Path(SQLITE_DB_URL.split("sqlite:///")[-1])
    remove_at_end = not db_file_path.exists()

    try:
        create_db_and_tables()

        # Check if the session is active
        session = next(get_session())
        assert session.is_active
        assert session.connection
        assert session.bind

        # Check if the tables are created
        metadata = inspect(sqlite_engine)
        for table in metadata.get_table_names():
            assert table in table_names

        # Check if the tables are empty and able to interact with the database
        try:
            session.exec(select(SmartAPIToken)).all()
        except Exception as e:
            assert False, f"Failed to interact with the database: {e}"
    finally:
        sqlite_engine.dispose()

        if remove_at_end:
            db_file_path.unlink()
