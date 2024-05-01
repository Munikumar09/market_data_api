from datetime import datetime

import pytest

from app.utils.common.exceptions import InvalidDateTimeFormatException
from app.utils.date_utils import validate_datetime_format


# Test cases for valid date and time formats
@pytest.mark.parametrize(
    "date_time, expected",
    [
        ("2024-04-30 21:10", datetime(2024, 4, 30, 21, 10)),
        ("2023/Apr/30 9:15", datetime(2023, 4, 30, 9, 15)),
        ("2021/April/30 21:10", datetime(2021, 4, 30, 21, 10)),
        ("2022-OCTOber-5 11:0", datetime(2022, 10, 5, 11, 0)),
    ],
)
# Test cases for valid datetime formats
def test_validate_datetime_format_valid(date_time, expected):
    """
    Test for valid datetime formats
    """
    assert validate_datetime_format(date_time) == expected


# Test cases for invalid date formats
@pytest.mark.parametrize(
    "date_time",
    [
        "30-04-2024 21:10",
        "04/30/2024 21:10",
        "2024/30/Apr 21:10",
        "2023_3/2 12:32",
        "2022-3-4T3:21",
        "2024/30/Apr 21-10",
        "2024/30/Apr-21:10",
    ],
)
def test_validate_datetime_format_invalid(date_time):
    """
    Test for invalid datetime formats
    """
    with pytest.raises(InvalidDateTimeFormatException) as excinfo:
        validate_datetime_format(date_time)
    assert excinfo.value.status_code == 400
    assert (
        f"Given datetime format {date_time} is invalid. "
        "Please provide a valid datetime that should be in the form 'year-month-day hour:minute'."
    ) in str(excinfo.value.detail)


# Test cases for edge cases
@pytest.mark.parametrize(
    "date_time",
    [
        "2024-04-31 21:10",  # Invalid day
        "2022-13-30 21:10",  # Invalid month
        "2023-02-29 21:10",  # Invalid leap year date
        "2021-02-29 40:10",  # invalid hours
        "2020-02-29 21:71",  # invalid minutes
    ],
)
def test_validate_datetime_format_edge_cases(date_time):
    """
    Test for edge cases like invalid day or month or year or time.
    """
    with pytest.raises(InvalidDateTimeFormatException) as excinfo:
        validate_datetime_format(date_time)
    assert excinfo.value.status_code == 400
    assert (
        f"Given datetime format {date_time} is invalid. "
        "Please provide a valid datetime that should be in the form 'year-month-day hour:minute'."
    ) in str(excinfo.value.detail)
