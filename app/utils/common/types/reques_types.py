# pylint: disable=missing-class-docstring
from enum import Enum

from app.utils.common.exceptions import IntervalNotFoundException


class RequestType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class CandlestickInterval(Enum):
    """Enumeration class representing candlestick intervals.

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

        Parameters:
        -----------
        interval: `str`
            The interval string to validate.

        Exceptions:
        -----------
        IntervalNotFoundException:
            If the interval is not a valid enum member.

        Return:
        -------
        str
            The enum member corresponding to the validated interval.
        """
        try:
            # Normalize the interval string
            normalized_interval = interval.replace(" ", "_").replace("-", "_").upper()
            # Return the enum member if valid
            return CandlestickInterval[normalized_interval]
        except KeyError as exc:
            # Raise an exception if the interval is not a valid enum member
            raise IntervalNotFoundException(interval) from exc
