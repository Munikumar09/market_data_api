import pytest

from app.utils.common.exceptions import IntervalNotFoundException
from app.utils.common.types.reques_types import CandlestickInterval


# Test cases for valid intervals
@pytest.mark.parametrize(
    "interval, expected",
    [
        ("1minute", CandlestickInterval.ONE_MINUTE),
        ("3min", CandlestickInterval.THREE_MINUTE),
        ("tenminute", CandlestickInterval.TEN_MINUTE),
        ("30min", CandlestickInterval.THIRTY_MINUTE),
        ("1hr", CandlestickInterval.ONE_HOUR),
        ("1d", CandlestickInterval.ONE_DAY),
        ("oneday", CandlestickInterval.ONE_DAY),
    ],
)
def test_validate_interval_valid(interval: str, expected: CandlestickInterval):
    """Test cases for valid intervals.

    Parameters:
    -----------
    interval: `str`
        Input interval of the candlestick.
    expected: `CandlestickInterval`
        Expected CandlestickInterval corresponding to the given input interval.
    """
    assert CandlestickInterval.validate_interval(interval) == expected


# Test cases for intervals with spaces, hyphens, underscores, and trailing 's'
@pytest.mark.parametrize(
    "interval, expected",
    [
        ("1 min", CandlestickInterval.ONE_MINUTE),
        ("1-minute", CandlestickInterval.ONE_MINUTE),
        ("one_minute", CandlestickInterval.ONE_MINUTE),
        ("5MINS", CandlestickInterval.FIVE_MINUTE),
        ("1 hr", CandlestickInterval.ONE_HOUR),
        ("ONE HOUR", CandlestickInterval.ONE_HOUR),
        ("1_D", CandlestickInterval.ONE_DAY),
    ],
)
def test_validate_interval_variations(interval: str, expected: CandlestickInterval):
    """Test cases for intervals with spaces, hyphens, underscores, and trailing 's'.

    Parameters:
    -----------
    interval: `str`
        Input interval of the candlestick.
    expected: `CandlestickInterval`
        Expected CandlestickInterval corresponding to given input interval.
    """
    assert CandlestickInterval.validate_interval(interval) == expected


# Test cases for invalid intervals
@pytest.mark.parametrize(
    "interval",
    [
        "2min",
        "invalid",
        "30 sec",
    ],
)
def test_validate_interval_invalid(interval: str):
    """Test cases for invalid intervals.

    Parameters:
    -----------
    interval: `str`
        Input interval of the candlestick.
    """
    with pytest.raises(IntervalNotFoundException) as excinfo:
        CandlestickInterval.validate_interval(interval)
    assert excinfo.value.status_code == 404
    assert (
        f"Candlestick interval {interval} not found. Please provide a valid interval."
        in str(excinfo.value.detail)
    )
