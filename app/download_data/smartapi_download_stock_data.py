import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from icecream import ic
from tqdm import tqdm


def search_valid_date(start_date, end_date, stock_symbol):
    valid_date = end_date
    while start_date <= end_date:
        try:
            total_days = (end_date - start_date).days
            middle_date = start_date + timedelta(days=total_days // 2)
            first_day = middle_date.replace(day=1)
            last_day = (middle_date + timedelta(days=31)).replace(day=1) - timedelta(
                days=1
            )
            stocks_url = f"http://127.0.0.1:8000/smart-api/equity/history/{stock_symbol}?interval=ONE_MINUTE&start_date={first_day.strftime('%Y-%m-%d')}%2009%3A15&end_date={last_day.strftime('%Y-%m-%d')}%2015%3A29"
            ic(first_day, last_day, stocks_url)
            response = requests.get(stocks_url, timeout=(60, 60))
            ic(response)
            if response.status_code == 200:
                if response.json() is None:
                    start_date = last_day + timedelta(days=1)
                else:
                    end_date = first_day - timedelta(days=1)
                    valid_date = first_day
            else:
                start_date = (start_date + timedelta(days=31)).replace(day=1)
            time.sleep(0.2)
        except:
            start_date = (start_date + timedelta(days=31)).replace(day=1)
            continue
    return valid_date


def download_stock_data():
    df = pd.read_csv(
        "/home/munikumar/Desktop/market_data_api/app/data/nse/ind_nifty500list.csv"
    )
    stocks_symbols = df["Symbol"].tolist()
    start_date = datetime(2016, 1, 1)
    end_date = datetime(2024, 3, 1)
    for stock_symbol in tqdm(stocks_symbols):
        dir_path = f"/home/munikumar/Desktop/market_data_api/app/data/historical_data/stocks/{stock_symbol}"
        if Path(dir_path).exists():
            continue
        list_date = start_date
        list_date_url = f"http://127.0.0.1:8000/nse/equity/listing/{stock_symbol}"
        list_date_request = requests.get(list_date_url, timeout=(60, 60))
        if list_date_request.status_code == 200:
            list_date = datetime.strptime(list_date_request.json(), "%d-%b-%Y")
        current_date = search_valid_date(list_date, end_date, stock_symbol)
        ic(list_date, stock_symbol, start_date, current_date)
        while current_date <= end_date:
            try:
                first_day = current_date.strftime("%Y-%m-%d")
                last_day = (
                    (current_date + timedelta(days=31)).replace(day=1)
                    - timedelta(days=1)
                ).strftime("%Y-%m-%d")
                stocks_url = f"http://127.0.0.1:8000/smart-api/equity/history/{stock_symbol}?interval=ONE_MINUTE&start_date={first_day}%2009%3A15&end_date={last_day}%2015%3A29"
                response = requests.get(stocks_url, timeout=(60, 60))
                if response.status_code == 200:
                    data = response.json()
                    if data is not None:
                        if not os.path.exists(dir_path):
                            os.makedirs(dir_path)
                        df = pd.DataFrame(data)
                        df.rename(
                            {
                                0: "timestamp",
                                1: "open",
                                2: "high",
                                3: "low",
                                4: "close",
                                5: "volume",
                            },
                            axis=1,
                            inplace=True,
                        )
                        df.to_csv(
                            f"{dir_path}/{current_date.strftime('%Y-%m')}.csv",
                            header=True,
                            index=False,
                        )
            except Exception as e:
                ic(e)
            finally:
                current_date = (
                    current_date.replace(day=1) + timedelta(days=31)
                ).replace(day=1)


if __name__ == "__main__":
    download_stock_data()
