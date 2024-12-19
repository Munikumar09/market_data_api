import os
from pathlib import Path
from urllib.parse import quote_plus

import psycopg2
import pytest
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from app.data_layer.database.db_connections.postgresql import (
    create_db_and_tables,
    get_session,
)
from app.utils.common.logger import get_logger
from app.utils.fetch_data import get_required_env_var

logger = get_logger(Path(__file__).name)

POSTGRES_USER = "POSTGRES_USER"
POSTGRES_PASSWORD = "POSTGRES_PASSWORD"
POSTGRES_HOST = "POSTGRES_HOST"
POSTGRES_PORT = "POSTGRES_PORT"
POSTGRES_DB = "POSTGRES_DB"


def create_database_if_not_exists():
    """Creates the database if it doesn't already exist and returns True if created, False otherwise."""
    conn = None
    try:
        conn = psycopg2.connect(
            user=get_required_env_var(POSTGRES_USER),
            password=get_required_env_var(POSTGRES_PASSWORD),
            host=get_required_env_var(POSTGRES_HOST),
            port=get_required_env_var(POSTGRES_PORT),
            database="postgres",
        )
        conn.autocommit = True

        cursor = conn.cursor()
        db_name = get_required_env_var(POSTGRES_DB)
        quoted_db_name = quote_plus(db_name)

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        db_exists = cursor.fetchone()

        if not db_exists:
            cursor.execute(f"CREATE DATABASE {quoted_db_name}")
            logger.info(f"Database '{db_name}' created.")
            return True  # Return True if the database was created
        else:
            logger.info(f"Database '{db_name}' already exists.")
            return False  # Return false if the database was not created

    except psycopg2.Error as e:
        logger.error(f"Error creating/checking database: {e}")
        raise
    finally:
        if conn:
            conn.close()


def drop_database_if_created(created: bool):
    """Drops the database only if it was created by the create_database_if_not_exists function."""
    if not created:
        logger.info("Skipping database drop as it was not created in this session.")
        return

    conn = None
    try:

        conn = psycopg2.connect(
            host=get_required_env_var(POSTGRES_HOST),
            port=get_required_env_var(POSTGRES_PORT),
            user=get_required_env_var(POSTGRES_USER),
            password=get_required_env_var(POSTGRES_PASSWORD),
            database="postgres",
        )
        conn.autocommit = True

        cursor = conn.cursor()
        db_name = get_required_env_var(POSTGRES_DB)
        quoted_db_name = quote_plus(db_name)

        # Terminate other sessions (same as before)
        cursor.execute(
            f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}';
        """
        )

        cursor.execute(f"DROP DATABASE {quoted_db_name}")
        logger.info(f"Database '{db_name}' dropped.")

    except psycopg2.Error as e:
        logger.error(f"Error dropping database: {e}")
        raise
    finally:
        if conn:
            conn.close()


def set_env_vars():
    """Set the environment variables required for the tests."""
    os.environ[POSTGRES_USER] = "muni123"
    os.environ[POSTGRES_PASSWORD] = "muni123"
    os.environ[POSTGRES_HOST] = "localhost"
    os.environ[POSTGRES_PORT] = "5432"
    os.environ[POSTGRES_DB] = "test_db"


def remove_env_vars():
    """Remove the environment variables required for the tests."""
    del os.environ[POSTGRES_USER]
    del os.environ[POSTGRES_PASSWORD]
    del os.environ[POSTGRES_HOST]
    del os.environ[POSTGRES_PORT]
    del os.environ[POSTGRES_DB]


table_names = {"smartapitoken", "instrumentprice", "user", "userverification"}


# Test the creation of the database and tables
def test_create_db_and_tables():
    """
    Test the create_db_and_tables function to ensure it creates the tables.
    """

    set_env_vars()
    created = create_database_if_not_exists()
    db_url = f"postgresql://{quote_plus(get_required_env_var(POSTGRES_USER))}:{quote_plus(get_required_env_var(POSTGRES_PASSWORD))}@{get_required_env_var(POSTGRES_HOST)}:{get_required_env_var(POSTGRES_PORT)}/{get_required_env_var(POSTGRES_DB)}"
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert tables == []
    create_db_and_tables(engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert set(tables) == table_names

    session = next(get_session(engine))

    assert session.is_active
    assert session.connection
    assert session.bind

    drop_database_if_created(created)
    remove_env_vars()


# # Test the session creation and handling
# def test_get_session(setup_database):
#     """
#     Test the get_session function to ensure it yields a session object.
#     """
#     session_generator = get_session()
#     session = next(session_generator)
#     assert isinstance(session, Session)
#     session_generator.close()

# # Test the logging of errors during database creation
# def test_create_db_and_tables_error(setup_database):
#     """
#     Test the create_db_and_tables function to ensure it logs an error if the database creation fails.
#     """
#     # Simulate an error by dropping the connection
#     engine.dispose()
#     with pytest.raises(Exception):
#         create_db_and_tables()

# # Test the logging of errors during session handling
# def test_get_session_error(setup_database):
#     """
#     Test the get_session function to ensure it logs an error if session creation fails.
#     """
#     # Simulate an error by dropping the connection
#     engine.dispose()
#     session_generator = get_session()
#     with pytest.raises(Exception):
#         next(session_generator)
