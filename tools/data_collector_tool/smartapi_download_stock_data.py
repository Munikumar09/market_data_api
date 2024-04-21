import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from tqdm import tqdm

from app.utils.common.types.reques_types import CandlestickInterval
from tools.utils.download_support_methods import (
    dataframe_to_json_files,
    search_valid_date,
)


def download_stock_data(interval: str):
    """Download the candlestick data of the given interval for the nifty 500 stocks"""

    valid_interval = CandlestickInterval.validate_interval(interval)
    df = pd.read_csv(
        "/home/munikumar/Desktop/market_data_api/app/data/nse/ind_nifty500list.csv"
    )
    stocks_symbols = df["Symbol"].tolist()
    start_date = datetime(2016, 1, 1)
    end_date = datetime(2024, 3, 1)
    for i, stock_symbol in enumerate(tqdm(stocks_symbols)):
        if i > 4:
            break
        dir_path = f"/home/munikumar/Desktop/market_data_api/app/data/historical_data/stocks/{stock_symbol}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        list_date = start_date
        list_date_url = f"http://127.0.0.1:8000/nse/equity/listing/{stock_symbol}"
        list_date_request = requests.get(list_date_url, timeout=(60, 60))
        if list_date_request.status_code == 200:
            list_date = datetime.strptime(list_date_request.json(), "%d-%b-%Y")
        current_date = search_valid_date(
            list_date, end_date, stock_symbol, valid_interval
        )
        while current_date <= end_date:
            try:
                first_day = current_date
                last_day = current_date + timedelta(days=valid_interval.value - 1)
                stocks_url = (
                    f"http://127.0.0.1:8000/smart-api/equity/history/{stock_symbol}?interval={valid_interval.name}&start_date="
                    f"{first_day.strftime('%Y-%m-%d')}%2000%3A00&end_date={last_day.strftime('%Y-%m-%d')}%2015%3A29"
                )
                response = requests.get(stocks_url, timeout=(60, 60))
                if response.status_code == 200:
                    data = response.json()
                    if data is not None:
                        df = pd.DataFrame(data)
                        dataframe_to_json_files(df, dir_path, valid_interval)
            except Exception as e:
                print(e)
            finally:
                current_date = last_day + timedelta(days=1)


if __name__ == "__main__":
    download_stock_data("one minute")
