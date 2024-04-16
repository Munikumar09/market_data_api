from fastapi import HTTPException, status


class SymbolNotFoundException(HTTPException):
    """
    SymbolNotFoundException is raised when the given symbol is not found in the stock exchange.
    """

    def __init__(self, symbol: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol {symbol} not found. Please provide a valid symbol. Refer to the NSE symbols list for valid symbols.",
        )


class CredentialsException(HTTPException):
    """
    CredentialsException is raised when the credentials are not set in the environment variable.
    """

    def __init__(self, credential_name: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{credential_name} environment variable is not set.",
        )


class IntervalNotFoundException(HTTPException):
    """
    IntervalNotFoundException is raised when the candlestick interval is not found in the intervals provided by the SmartApi.
    Refer this link: https://smartapi.angelbroking.com/docs/Historical and given examples for more information.
    """

    def __init__(self, interval: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candlestick interval {interval} not found. Please provide a valid interval.",
        )


class InvalidDateTimeFormatException(HTTPException):
    """
    InvalidDateTimeFormatException is raised when the given datetime format is invalid.
    """

    def __init__(self, date_date: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Given datetime format {date_date} is invalid. Please provide a valid datetime that should be in the form '%Y-%m-%d %H:%M'.",
        )


class InvalidDateRangeBoundsException(HTTPException):
    """
    InvalidDateRangeBoundsException is raised when the given datetime range is invalid for given interval.
    """

    def __init__(self, start_date: str, end_date: str, max_days: int, interval: str):
        super().__init__(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"The specified date range from {start_date} to {end_date} is invalid. Please ensure that the end date is greater than or equal to start date and difference between them does not exceed {max_days} for given interval {interval}.",
        )


class InvalidTradingHoursException(HTTPException):
    """
    InvalidTradingHoursException is raised for errors in the time accessed outside trading hours of stock market.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempted to access trading system outside of trading hours.",
        )


class AllDaysHolidayException(HTTPException):
    """Exception raised when all days in the given date range are market holidays."""

    def __init__(self, start_date: str, end_date: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All days from {start_date} to {end_date} are market holidays.",
        )


class DataUnavailableException(HTTPException):
    """DataUnavailableException raised when the requested data is not available from the SmartAPI."""

    def __init__(self, start_date: str, stock_symbol: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.get_detail(stock_symbol, start_date),
        )

    def get_detail(self, stock_symbol: str, start_date: str) -> str:
        if start_date is None:
            return f"No data available for this stock {stock_symbol}"
        return f"Data for the provided dates is unavailable; please use a date range starting from the {start_date} date onwards."
