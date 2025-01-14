"""
This script contains the CRUD operations for the Instrument table.
"""

from pathlib import Path

from sqlmodel import Session, delete, select

from app.data_layer.database.db_connections.postgresql import get_session
from app.data_layer.database.db_connections.sqlite import with_session
from app.data_layer.database.models import Instrument, InstrumentPrice
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


def deleted_all_data():
    """
    Deletes all data from the Instrument table.
    """
    with get_session() as session:
        statement = delete(Instrument)
        session.exec(statement)
        session.commit()


@with_session
def get_all_stock_price_info(session: Session) -> list[InstrumentPrice]:
    """
    Retrieve all the data from the InstrumentPrice table in the SQLite database.

    Parameters
    ----------
    session: ``Session``
        The SQLModel session object to use for the database operations

    Returns
    -------
    ``List[InstrumentPrice]``
        The list of all the InstrumentPrice objects present in the table
    """
    stmt = select(InstrumentPrice)
    return session.exec(stmt).all()  # type: ignore
