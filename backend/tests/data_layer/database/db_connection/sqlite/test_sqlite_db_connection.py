""" 
Test the database connection and interaction with the SQLite database.
"""

from pathlib import Path

from sqlmodel import create_engine, inspect, select

from app.data_layer.database.db_connections.sqlite import (
    create_db_and_tables,
    get_session,
    sqlite_engine,
)
from app.data_layer.database.models.smartapi_model import SmartAPIToken

table_names = {"smartapitoken", "instrumentprice", "user", "userverification"}


def test_database_init_and_interaction():
    """
    Test if the database is created and tables are created and empty and able to interact with the database.
    """
    engine = create_engine("sqlite:///:memory:")
    create_db_and_tables(engine)

    # Check if the tables are created
    db_tables = inspect(sqlite_engine).get_table_names()
    assert set(db_tables) == table_names

    with get_session(engine) as session:
        assert session.is_active
        assert session.connection
        assert session.bind

        # Check if the tables are empty
        try:
            session.exec(select(SmartAPIToken)).all()
        except Exception as e:
            assert False, f"Failed to interact with the database: {e}"
