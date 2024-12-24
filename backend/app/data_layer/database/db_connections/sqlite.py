""" 
This script is responsible for creating a connection to the SQLite database. 
It also provides a function to create the database and tables and a function
to get a session object to interact with the database.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)

from app.utils.urls import SQLITE_DB_URL

sqlite_engine = create_engine(SQLITE_DB_URL)


def create_db_and_tables(db_engine: Engine | None = None):
    """
    Create the database and tables if they do not exist
    """
    logger.info("Creating database and tables")

    # If the database engine is not provided, use the default engine
    db_engine = db_engine or sqlite_engine

    try:
        SQLModel.metadata.create_all(db_engine)
        logger.info("Database and tables created successfully")
    except Exception as e:
        logger.error("Failed to create database and tables: %s", e)
        raise


@contextmanager
def get_session(db_engine: Engine | None = None) -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures proper handling of commits and rollbacks.
    """
    db_engine = db_engine or sqlite_engine
    session = Session(db_engine)

    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.info("Session rollback due to error: %s", e)
        raise
    finally:
        session.close()
