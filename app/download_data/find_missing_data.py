import json
import os
import pathlib
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from icecream import ic
from smartapi_download_stock_data import search_valid_date
from tqdm import tqdm

end_date = datetime(2024,3,1)
directory = "app/data/historical_data/stocks/"
list_dates_dic = {}
for ind,foldername in enumerate(tqdm(os.scandir(directory))):
    if(ind<170):
        ic(foldername.name)
        continue
    start_date = datetime(2016,1,1)
    list_date = start_date
    list_date_url = f'http://127.0.0.1:8000/nse/equity/listing/{foldername.name}'
    list_date_request = requests.get(list_date_url,timeout=(60,60))
    if list_date_request.status_code==200:
        list_date = datetime.strptime(list_date_request.json(),'%d-%b-%Y')
    current_date = search_valid_date(list_date,end_date,foldername.name)
    list_dates_dic[foldername.name]=current_date
    while current_date<=end_date:
        json_data = {}
        if os.path.exists(f'{foldername.path}/{current_date.strftime("%Y-%m")}.json'):
            file_path = f'{foldername.path}/{current_date.strftime("%Y-%m")}.json'
        else:
            file_path = f'{foldername.path}/{current_date.strftime("%Y-%m")}.csv.json'
        first_day = current_date
        last_day = ((current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1))  
        try:
            if not os.path.exists(file_path):
                stocks_url = f"http://127.0.0.1:8000/smart-api/equity/history/{foldername.name}?interval=ONE_MINUTE&start_date={first_day.strftime('%Y-%m-%d')}%2009%3A15&end_date={last_day.strftime('%Y-%m-%d')}%2015%3A29"
                response = requests.get(stocks_url,timeout=(60,60))
                if response.status_code == 200:
                    data = response.json()
                    if data is None:
                        continue
                    else:
                        for row in data:
                            timestamp = row[0].split('T')[0]
                            time_value= row[0].split('T')[1].split(':00+')[0]
                            values = [row[1],row[2], row[3],row[4],row[5]]
                            if timestamp not in json_data:
                                json_data[timestamp] = {}
                            json_data[timestamp][time_value] = values

            else:
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                base_name = file_path.split('.')[0]
                # Create the new file name with the desired extension
                new_filename = base_name + ".json"

                # Rename the file
                os.rename(file_path, new_filename)
            while first_day <= last_day:
                try:
                    if json_data.get(first_day.strftime("%Y-%m-%d"))==None:
                        stocks_url = f"http://127.0.0.1:8000/smart-api/equity/history/{foldername.name}?interval=ONE_MINUTE&start_date={first_day.strftime('%Y-%m-%d')}%2009%3A15&end_date={first_day.strftime('%Y-%m-%d')}%2015%3A29"
                        response = requests.get(stocks_url,timeout=(60,60))
                        if response.status_code == 200:
                            data = response.json()
                            if data is None:
                                continue
                            else:
                                for row in data:
                                    timestamp = row[0].split('T')[0]
                                    time_value= row[0].split('T')[1].split(':00+')[0]
                                    values = [row[1],row[2],row[3],row[4],row[5]]
                                    if timestamp not in json_data:
                                        json_data[timestamp] = {}
                                    json_data[timestamp][time_value] = values
                except Exception as e:
                    ic('inner',e)
                finally:    
                    time.sleep(0.2)
                    first_day+=timedelta(days=1)       
            with open(f"{foldername.path}/{current_date.strftime('%Y-%m')}.json", "w") as json_file:
                json.dump(json_data, json_file, indent=4)
        except Exception as e:
            ic('outer',e)
        finally:
            current_date = (current_date.replace(day=1) + timedelta(days=31)).replace(day=1)
with open('listing_dates.json','w') as json_file:
    json.dump(list_dates_dic,json_file,indent=4)