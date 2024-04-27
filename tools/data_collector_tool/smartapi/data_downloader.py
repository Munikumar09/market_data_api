# pylint: disable=too-many-locals
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

from app.utils.common.types.reques_types import CandlestickInterval
from app.utils.file_utils import load_json_data
from tools.data_collector_tool.smartapi.constants import (
    DATA_DOWNLOAD_PATH,
    DATA_STARTING_DATES_PATH,
    NIFTY_500_STOCK_LIST_PATH,
)
from tools.data_collector_tool.smartapi.data_downloader_utils import (
    dataframe_to_json_files,
)


def download_nifty500_stock_data(interval: str):
    """Download the candlestick data of the given interval for the nifty 500 stocks"""

    valid_interval = CandlestickInterval.validate_interval(interval)

    # Load nifty 500 stocks symbols from the given csv file.
    df = pd.read_csv(NIFTY_500_STOCK_LIST_PATH)
    stocks_symbols = df["Symbol"].tolist()

    # Initialize default start and end dates which are used to determine actual data availability dates of given interval.
    end_date = datetime.now()
    data_starting_dates = load_json_data(DATA_STARTING_DATES_PATH)
    # Traverse the list of stocks and download each stock data.
    for stock_symbol in tqdm(stocks_symbols):
        # Get the date from which the data starts available for the given stock symbol and interval.
        start_date = data_starting_dates.get(stock_symbol).get(valid_interval.name)
        if not start_date:
            continue
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        # Destination location to store the downloaded stock data.
        dir_path = Path(f"{DATA_DOWNLOAD_PATH}/{stock_symbol}")
        # Create a directory if it doesn't exist.
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Traverse the dates and download the data of the given stock and interval.
        for next_day in range(
            0, (end_date - start_date).days + 1, valid_interval.value[1]
        ):
            first_day = start_date + timedelta(days=next_day)
            last_day = first_day + timedelta(days=valid_interval.value[1] - 1)
            stocks_url = (
                f"http://127.0.0.1:8000/smart-api/equity/history/{stock_symbol}?interval={valid_interval.name}&start_date="
                f"{first_day.strftime('%Y-%m-%d')}%2000%3A00&end_date={last_day.strftime('%Y-%m-%d')}%2015%3A29"
            )
            try:
                response = requests.get(stocks_url, timeout=(60, 60))
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        df = pd.DataFrame(data["available_stock_data"])
                        dataframe_to_json_files(df, dir_path, valid_interval)
            except Exception as e:
                print(e)
            break


if __name__ == "__main__":
    download_nifty500_stock_data("one minute")
