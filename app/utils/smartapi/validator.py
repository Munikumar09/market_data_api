# pylint: disable=chained-comparison
from bisect import bisect_left
from datetime import datetime, time, timedelta
from typing import Tuple

from app.utils.common.exceptions import (
    AllDaysHolidayException,
    DataUnavailableException,
    InvalidDateRangeBoundsException,
    InvalidTradingHoursException,
    SymbolNotFoundException,
)
from app.utils.common.types.financial_types import Exchange
from app.utils.common.types.reques_types import CandlestickInterval
from app.utils.date_utils import validate_datetime_format
from app.utils.file_utils import get_symbols, load_json_data, read_text_data
from app.utils.smartapi.constants import (
    BSE_SYMBOLS_PATH,
    DATA_STARTING_DATES_PATH,
    NSE_HOLIDAYS_PATH,
    NSE_SYMBOLS_PATH,
)


def validate_symbol_and_get_token(
    stock_exchange: Exchange, stock_symbol: str
) -> Tuple[str, str]:
    """
    Validate the stock symbol and get the stock token from the symbols data.
    Ref NSE website for information about stock symbols.

    Parameters:
    -----------
    stock_exchange: ``Exchange``
        The stock exchange of the stock symbol
    stock_symbol: ``str``
        The stock symbol to be validated and get the token

    Raises:
    -------
    ``SymbolNotFoundException``
        If the stock symbol is not found in the symbols data

    Returns:
    --------
    Tuple[str, str]
        The stock token and the stock symbol

    """
    symbols_path = BSE_SYMBOLS_PATH

    if stock_exchange == Exchange.NSE:
        symbols_path = NSE_SYMBOLS_PATH
        stock_symbol = stock_symbol.upper() + "-EQ"

    all_symbols_data = get_symbols(symbols_path)

    if stock_symbol not in all_symbols_data:
        raise SymbolNotFoundException(stock_symbol.split("-")[0])

    return all_symbols_data[stock_symbol], stock_symbol


def check_market_open_between_dates(start_date: datetime, end_date: datetime):
    """Checks whether the stock market is open between the given dates.

    Parameters:
    -----------
    start_date: ``datetime``
        Start date.
    end_date: ``datetime``
        End date.

    Exceptions:
    -----------
    ``AllDaysHolidayException``
        Raised when all days in the given date range are market holidays.
    """
    # Read the holidays data into list
    holidays_data = read_text_data(NSE_HOLIDAYS_PATH)
    # Check for any market open day between given dates.
    # If you find any open day then definitely the data is not empty otherwise raise an error.
    current_date = start_date
    while current_date <= end_date:
        index = bisect_left(holidays_data, current_date.strftime("%Y-%m-%d"))
        if (
            current_date.weekday() < 5
            and index != len(holidays_data)
            and holidays_data[index] != current_date.strftime("%Y-%m-%d")
        ):
            return
        current_date += timedelta(days=1)
    raise AllDaysHolidayException(
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )


def check_data_availability(end_date: datetime, stock_symbol: str):
    """Check whether the data is available or not for the requested dates from the SmartAPI.

    Parameters:
    -----------
    end_date: ``datetime``
        End date
    stock_symbol: ``str``
        Symbol of the stock.

    Exceptions:
    -----------
    ``DataUnavailableException``
        Raised when the data is unavailable for the requested dates from the SmartAPI.
    """
    # If end date is less than the date from where the data availability starts, then
    # no data can be retrieved; therefore, an error should be raised.
    data_starting_dates = load_json_data(DATA_STARTING_DATES_PATH)
    starting_date = data_starting_dates.get(stock_symbol)
    if starting_date is None or end_date < datetime.strptime(starting_date, "%Y-%m-%d"):
        raise DataUnavailableException(starting_date, stock_symbol)


def validate_date_range(
    from_date: str, to_date: str, interval: CandlestickInterval, stock_symbol: str
) -> Tuple[str, str]:
    """
    Validate given dates and their range.

    Parameters:
    -----------
    from_date: ``str``
        Start date and time to be validated.
    to_date: ``str``
        End date and time to be validated.
    interval: ``str``
        candlestick interval.

    Exceptions:
    -----------
    ``InvalidDateRangeBoundsException``
        If the specified date range is invalid for given interval.

    InvalidTradingHoursException:
        If the time accessed outside trading hours of stock market.

    Return:
    -------
    Tuple[str, str]
        validated start and end dates.
    """
    start_date = validate_datetime_format(from_date)
    end_date = validate_datetime_format(to_date)

    # check data is available or not between given dates.
    check_data_availability(end_date, stock_symbol)

    # check given dates range are market holidays or not.
    check_market_open_between_dates(start_date, end_date)

    # check given timings are market active trading hours.
    start_time = time(9, 15)
    end_time = time(15, 29)
    if (start_date.time() < start_time or start_date.time() > end_time) and (
        end_date.time() < start_time or end_date.time() > end_time
    ):
        raise InvalidTradingHoursException()

    # check date range should not exceed specific days per request based on given interval.
    total_days = (end_date - start_date).days
    if total_days >= 0 and total_days <= interval.value:
        return start_date.strftime("%Y-%m-%d %H:%M"), end_date.strftime(
            "%Y-%m-%d %H:%M"
        )
    raise InvalidDateRangeBoundsException(
        from_date, to_date, interval.value, interval.name
    )
