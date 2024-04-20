import os
import time
from datetime import datetime, timedelta

import pandas as pd
import requests
from tqdm import tqdm

from app.utils.common.types.reques_types import CandlestickInterval
from app.utils.file_utils import load_json_data, write_to_json_file


def search_valid_date(
    start_date: datetime,
    end_date: datetime,
    stock_symbol: str,
    interval: CandlestickInterval,
) -> datetime:
    """It finds the valid month from where the availability of data starts for the given stock symbol and interval by using binary search method.

    Parameters:
    -----------
    start_date: `datetime`
        Start date to search.
    end_date: `datetime`
        End date to search.
    stock_symbol: `str`
        The symbol of the stock.

    Return:
    -------
    datetime
        searched month from where the availability of data starts for the given stock symbol and interval.
    """
    valid_date = end_date
    while start_date <= end_date:
        try:
            total_days = (end_date - start_date).days
            middle_date = start_date + timedelta(days=total_days // 2)
            first_day = middle_date.replace(day=3)
            last_day = (middle_date + timedelta(days=31)).replace(day=1) - timedelta(
                days=1
            )
            stocks_url = f"http://127.0.0.1:8000/smart-api/equity/history/{stock_symbol}?interval={interval.name}&start_date={first_day.strftime('%Y-%m-%d')}%2009%3A15&end_date={last_day.strftime('%Y-%m-%d')}%2015%3A29"
            response = requests.get(stocks_url, timeout=(60, 60))
            if response.status_code == 200 and response.json():
                end_date = first_day - timedelta(days=3)
                valid_date = first_day.replace(day=1)
            else:
                start_date = last_day + timedelta(days=1)
            time.sleep(0.2)
        except:
            start_date = last_day + timedelta(days=1)
            continue
    return valid_date


def dataframe_to_json_files(
    df: pd.DataFrame, dir_path: str, interval: CandlestickInterval
):
    """Process the given dataframe and convert it into suitable data structure i.e dictionary which will be stored in json file.

    Parameters:
    -----------
    df: `pd.DataFrame`
        pandas DataFrame to store into json files.
    dir_path: `str`
        Path of the destination directory to store json files.
    """
    # Convert timestamp to datetime and extract year and day
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["year"] = df["timestamp"].dt.year
    df["day"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    if interval.name == "ONE_DAY":
        grouped = df.groupby("year")

        # Iterate over each group
        for year, group in grouped:
            # Prepare data for JSON
            data = (
                group.set_index("day")
                .drop(columns=["year", "timestamp"])
                .to_dict(orient="index")
            )
            # Load
            json_file_path = f"{dir_path}/{str(year)}.json"
            if os.path.exists(json_file_path):
                stored_data = load_json_data(json_file_path)
                stored_data.update(data)
                data = stored_data
            write_to_json_file(json_file_path, data)
    else:
        df["time"] = df["timestamp"].dt.strftime("%H:%M")

        # Group by year and day
        grouped = df.groupby(["year", "day"])

        # Iterate over each group
        for (year, day), group in grouped:
            # Create directory for the year if it doesn't exist
            year_dir = f"{dir_path}/{str(year)}"
            if not os.path.exists(year_dir):
                os.makedirs(year_dir)

            # Prepare data for JSON
            data = (
                group.set_index("time")
                .drop(columns=["year", "day", "timestamp"])
                .to_dict(orient="index")
            )
            # Write to JSON file
            json_file_path = os.path.join(year_dir, f"{day}.json")
            write_to_json_file(json_file_path, data)


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
                stocks_url = f"http://127.0.0.1:8000/smart-api/equity/history/{stock_symbol}?interval={valid_interval.name}&start_date={first_day.strftime('%Y-%m-%d')}%2000%3A00&end_date={last_day.strftime('%Y-%m-%d')}%2015%3A29"
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
