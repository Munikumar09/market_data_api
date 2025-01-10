"""
This script contains the CRUD operations for the Instrument table.
"""

from pathlib import Path
from typing import Sequence, cast

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import delete, or_, select, Session

from app.data_layer.database.db_connections.sqlite import get_session
from app.data_layer.database.models import Instrument, InstrumentPrice
from app.utils.common.logger import get_logger


from sqlalchemy.dialects.sqlite import insert

from app.data_layer.database.db_connections.sqlite import with_session


logger = get_logger(Path(__file__).name)

################### Instrument CRUD Operations ###################


def deleted_all_data():
    """
    Deletes all data from the Instrument table.
    """
    with get_session() as session:
        statement = delete(Instrument)
        session.exec(statement)
        session.commit()


def insert_data(
    data: Instrument | list[Instrument],
    remove_existing: bool = False,
):
    """
    Inserts data into the Instrument table.

    Parameters
    ----------
    data: ``Instrument`` | ``List[Instrument]``
        The data to insert into the table.
    remove_existing: ``bool``
        If True, all existing data in the table will be deleted before inserting the new data.
    """
    if isinstance(data, Instrument):
        data = [data]

    if remove_existing:
        logger.warning("Removing existing data from Instrument table...")
        deleted_all_data()

    with get_session() as session:
        session.add_all(data)
        session.commit()
        session.close()


def get_conditions_list(condition_attributes: dict[str, str]) -> list[BinaryExpression]:
    """
    Generate a list of conditions based on the provided attributes.

    This function takes a dictionary of attributes and their corresponding values as input.
    It generates a list of SQLAlchemy BinaryExpression objects, which can be used as conditions
    in a database query.

    Parameters
    ----------
    condition_attributes: ``dict[str, str]``
        A dictionary of attributes and their corresponding values

    Returns
    -------
    conditions: ``list[BinaryExpression]``
        A list of SQLAlchemy BinaryExpression objects
    """
    conditions = []

    for key, value in condition_attributes.items():
        if value:
            try:
                conditions.append(getattr(Instrument, key) == value)
            except AttributeError:
                logger.exception(
                    "Attribute %s not found in Instrument model, skipping...", key
                )

    return conditions


def get_smartapi_tokens_by_any_condition(**kwargs) -> Sequence[Instrument]:
    """
    Retrieve a list of Instrument objects based on the specified conditions.
    The possible keyword arguments are the attributes of the Instrument model.
    The function returns a list of Instrument objects that match any of the
    specified conditions. Refer Instrument model for the attributes.

    Parameters
    ----------
    **kwargs: ``Dict[str, str]``
        The attributes and their corresponding values to filter the data.
        The attributes should be the columns of the Instrument model

    Returns
    -------
    result: ``List[Instrument]``
        A list of Instrument objects that match the any of the specified conditions

    >>> Example:
    >>> get_smartapi_tokens_by_any_condition(symbol="INFY", exchange="NSE")
    >>> [Instrument(symbol='INFY', exchange='NSE', token='1224', ...),
            Instrument(symbol='TCS', exchange='NSE', token='1225', ...), ...]

    The above example will return all the Instrument objects with symbol 'INFY' or
    exchange 'NSE'.
    """
    with get_session() as session:
        conditions = get_conditions_list(kwargs)

        statement = select(Instrument).where(
            or_(*conditions)  # pylint: disable=no-value-for-parameter
        )
        result = session.exec(statement).all()

        return result


def get_smartapi_tokens_by_all_conditions(
    **kwargs,
) -> Sequence[Instrument]:
    """
    Retrieve a list of Instrument objects based on the specified conditions.
    The possible keyword arguments are the attributes of the Instrument model.
    The function returns a list of Instrument objects that match all of the
    specified conditions. Refer Instrument model for the attributes.

    Parameters
    ----------
    **kwargs: ``Dict[str, str]``
        The attributes and their corresponding values to filter the data.
        The attributes should be the columns of the Instrument model

    Returns
    -------
    result: ``List[Instrument]``
        A list of Instrument objects that match the all of the specified conditions

    >>> Example:
    >>> get_smartapi_tokens_by_all_conditions(symbol="INFY", exchange="NSE")
    >>> [Instrument(symbol='INFY', exchange='NSE', token='1224', ...)]

    The above example will return all the Instrument objects with symbol 'INFY' and
    exchange 'NSE'.
    """
    with get_session() as session:
        conditions = get_conditions_list(kwargs)
        statement = select(Instrument).where(*conditions)
        result = session.exec(statement).all()

    return result


################### InstrumentPrice CRUD Operations ###################


@with_session
def upsert(
    stock_price_info: dict[str, str | None] | list[dict[str, str | None]],
    session: Session,
):
    """
    Upsert means insert the data into the table if it does not already exist.
    If the data already exists, it will be updated with the new data

    Example:
    --------
    >>> If the table has the following data:
    | id | symbol | price |
    |----|--------|-------|
    | 1  | AAPL   | 100   |
    | 2  | MSFT   | 200   |

    >>> If the following data is upserted:
    | id | symbol | price |
    |----|--------|-------|
    | 1  | AAPL   | 150   |
    | 3  | GOOGL  | 300   |

    >>> The table will be updated as:
    | id | symbol | price |
    |----|--------|-------|
    | 1  | AAPL   | 150   |
    | 2  | MSFT   | 200   |
    | 3  | GOOGL  | 300   |

    Parameters
    ----------
    stock_price_info: ``dict[str, str|None]| list[dict[str, str|None]]``
        The InstrumentPrice objects to upsert into the table
    session: ``Session``
        The SQLModel session object to use for the database operations
    """
    upsert_stmt = insert(InstrumentPrice).values(stock_price_info)

    # Create a dictionary of columns to update if the data already exists
    columns = {
        column.name: getattr(upsert_stmt.excluded, column.name)
        for column in upsert_stmt.excluded
    }
    upsert_stmt = upsert_stmt.on_conflict_do_update(set_=columns)

    session.exec(upsert_stmt)  # type: ignore
    session.commit()


@with_session
def insert_or_ignore(
    stock_price_info: dict[str, str | None] | list[dict[str, str | None]],
    session: Session,
):
    """
    Add the provided data into the StockPriceInfo table if the data does not already exist.
    If the data already exists, it will be ignored.

    Parameters
    ----------
    stock_price_info: ``dict[str, str|None]| list[dict[str, str|None]]``
        The InstrumentPrice objects to insert into the table
    session: ``Session``
        The SQLModel session object to use for the database operations
    """
    insert_stmt = insert(InstrumentPrice).values(stock_price_info)
    insert_stmt = insert_stmt.on_conflict_do_nothing()

    session.exec(insert_stmt)  # type: ignore
    session.commit()


@with_session
def instrumentprice_insert_data(
    data: (
        InstrumentPrice
        | dict[str, str | None]
        | list[InstrumentPrice | dict[str, str | None]]
        | None
    ),
    session: Session,
    update_existing: bool = False,
):
    """
    Insert the provided data into the InstrumentPrice table in the SQLite database. It
    will handle both single and multiple data objects. If the data already exists in the table,
    it will either update the existing data or ignore the new data based on the value of the
    `update_existing` parameter

    Parameters
    ----------
    data: ``InstrumentPrice | dict[str, str|None] | List[InstrumentPrice | dict[str, str | None]] | None``
        The data to insert into the table
    session: ``Session``
        The SQLModel session object to use for the database operations. If not provided,
        a new session will be created from the database connection pool
    update_existing: ``bool``, ( defaults = False )
        If True, the existing data in the table will be updated with the new data
    """
    if not data:
        logger.warning("Provided data is empty. Skipping insertion.")
        return

    if isinstance(data, (InstrumentPrice, dict)):
        data = [data]

    # Convert list of InstrumentPrice to a list of dicts
    data_to_insert = cast(
        list[dict[str, str | None]],
        [
            item.to_dict() if isinstance(item, InstrumentPrice) else item
            for item in data
        ],
    )

    if update_existing:
        upsert(data_to_insert, session=session)
    else:
        insert_or_ignore(data_to_insert, session=session)


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
