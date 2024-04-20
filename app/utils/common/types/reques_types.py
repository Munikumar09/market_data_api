# pylint: disable=missing-class-docstring
from enum import Enum

from app.utils.common.exceptions import IntervalNotFoundException


class RequestType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class CandlestickInterval(Enum):
    """
    Enumeration class representing candlestick intervals.

    Each member corresponds to a specific time interval and its associated value.
    """

    ONE_MINUTE = 30
    THREE_MINUTE = 60
    FIVE_MINUTE = 100
    TEN_MINUTE = 100
    FIFTEEN_MINUTE = 200
    THIRTY_MINUTE = 200
    ONE_HOUR = 400
    ONE_DAY = 2000

    @staticmethod
    def validate_interval(interval: str) -> "CandlestickInterval":
        """
        Validates an interval string and returns the corresponding enum member.

        Args:
            interval (str): The interval string to validate (e.g., "one minute", "15m").

        Returns:
            CandlestickInterval: The enum member corresponding to the validated interval.

        Raises:
            ValueError: If the interval is not a valid enum member.
        """
        possible_input_intervals = (
            ("1min", "1minute", "oneminute", CandlestickInterval.ONE_MINUTE),
            ("3min", "3minute", "threeminute", CandlestickInterval.THREE_MINUTE),
            ("5min", "5minute", "fiveminute", CandlestickInterval.FIVE_MINUTE),
            ("10min", "10minute", "tenminute", CandlestickInterval.TEN_MINUTE),
            ("15min", "15minute", "fifteenminute", CandlestickInterval.FIFTEEN_MINUTE),
            ("30min", "30minute", "thirtyminute", CandlestickInterval.THIRTY_MINUTE),
            ("1day", "1d", "oneday", CandlestickInterval.ONE_DAY),
        )
        # Normalize the interval string
        normalized_interval = (
            interval.lower().replace(" ", "").replace("-", "").replace("_", "")
        )
        if normalized_interval.endswith("s"):
            normalized_interval = normalized_interval[:-1]
        for input_interval in possible_input_intervals:
            if normalized_interval in input_interval:
                return input_interval[3]
        raise IntervalNotFoundException(interval)
