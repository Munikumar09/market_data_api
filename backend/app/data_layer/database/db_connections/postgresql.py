from pathlib import Path
from typing import Generator
from urllib.parse import quote_plus

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.data_layer.database.models import *
from app.utils.common.logger import get_logger
from app.utils.fetch_data import get_required_env_var

logger = get_logger(Path(__file__).name)


# Get the database connection details from the environment variables
user_name = get_required_env_var("POSTGRES_USER")
password = get_required_env_var("POSTGRES_PASSWORD")
host = get_required_env_var("POSTGRES_HOST")
port = get_required_env_var("POSTGRES_PORT")
db_name = get_required_env_var("POSTGRES_DB")

DATABASE_URL = f"postgresql://{quote_plus(user_name)}:{quote_plus(password)}@{host}:{port}/{db_name}"


engine = create_engine(DATABASE_URL)


def create_db_and_tables(db_engine: Engine | None = None):
    """
    Create the database and tables if they do not exist
    """
    logger.info("Creating database and tables")

    if not db_engine:
        db_engine = engine

    try:
        SQLModel.metadata.create_all(db_engine)
        logger.info("Database and tables created successfully")
    except Exception as e:
        logger.error("Failed to create database and tables: %s", e)
        raise


def get_session(db_engine: Engine | None = None) -> Generator[Session, None, None]:
    """
    Create a new session and return it
    """
    if not db_engine:
        db_engine = engine

    with Session(db_engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error: %s", e)
            raise