from datetime import datetime, timedelta
import statistics
from src.task1 import data_queue

class DataBucket:
    def __init__(self, first_time):
        self.rows = []
        self.open_time = first_time + timedelta(seconds=1)
        self.close_time = first_time
        self.open_price = None
        self.close_price = None
        self.high_price = 0
        self.low_price = 999999999999999999999999
        self.volume =  0
    def ohlcv_bucket(self, curr_time, price, volume, row):
        if curr_time < self.open_time:
            self.open_time = curr_time
            self.open_price = price
        if curr_time > self.close_time:
            self.close_time = curr_time
            self.close_price = price
        if price > self.high_price:
            self.high_price = price
        if price < self.low_price:
            self.low_price = price
        self.volume += volume
        self.rows.append(row)
        # print(f"curr_time: {curr_time} open_time: {self.open_time} close_time: {self.close_time} open_price: {self.open_price} close_price: {self.close_price}")

def data_clean(data_dict):
    price_upper_bound = 500
    price_lower_bound = 400
    volume_lower_bound = 10
    price_outlier_flag = []
    duplicates = {}
    seen_keys = set()
    price_window = [float(data_queue.queue[0][1])]
    volume_window = [int(data_queue.queue[0][2])]
    volume_outlier_window = data_queue.qsize()*.1
    market_open_hour = 9
    market_open_minute = 30
    market_close_hour = 16
    market_close_minute = 30
    i = 0
    price_outlier_window = (data_queue.qsize())*.10
    while not data_queue.empty():
        i += 1
        input_str = data_queue.get()
        try:
            row_timestamp = datetime.strptime(input_str[0], "%Y-%m-%d %H:%M:%S.%f")
            key = row_timestamp.replace(microsecond=0)
        except ValueError:
            print(f"time error!")
            continue
        # Skip data that is after market hours or before market open
        hour = row_timestamp.hour
        minute = row_timestamp.minute
        if hour > market_close_hour and minute > market_close_minute or hour < market_open_hour and minute < market_open_hour:
            # print(f"Skipped data outside regular market hours: {row_timestamp}")
            continue
        timestamp_str = input_str[0].strip() if input_str[0] else None
        price_str = input_str[1].strip() if input_str[1] else None
        volume_str = input_str[2].strip() if input_str[2] else None
        # Skip if any of the fields are None or empty
        if not timestamp_str or not price_str or not volume_str:
            continue
        # rows[0] = row_timestamp.strftime("%f")
        price_outlier_calculator = float(input_str[1])
        volume_outlier_calculator = int(input_str[2])
        if len(price_window) > price_outlier_window:
            price_window.pop(0)
        if i >= price_outlier_window:
            i = 0
            price_q1 = statistics.quantiles(price_window, n=4)[0]
            price_q3 = statistics.quantiles(price_window, n=4)[2]
            price_iqr = price_q3 - price_q1
            price_lower_bound = price_q1 - 5 * price_iqr
            price_upper_bound = price_q3 + 5 * price_iqr
        if volume_outlier_calculator < volume_lower_bound:
            # print(f"cleaned low volume:{volume_outlier_calculator} under {volume_lower_bound}")
            continue
        if price_outlier_calculator < price_lower_bound or price_outlier_calculator > price_upper_bound:
            price_outlier_flag.append(input_str)
            # print(f"Outlier detected! {input_str} with bounds {price_lower_bound} and {price_upper_bound}")
            continue  # Skip adding this outlier value
            # Append only valid numbers
        # key = row_timestamp.strftime("%Y%m%d%H%M%S")
        if row_timestamp in seen_keys:
            # print(f"duplicate value found: {input_str}")
            if input_str[0] not in duplicates:
                duplicates[input_str[0]] = []
            duplicates[input_str[0]].append(input_str)
            continue
        elif key not in data_dict.data_list.keys():
            data_dict.data_list[key] = DataBucket(key)
        price = float(price_str)
        volume = int(volume_str)
        data_dict.data_list.get(key).ohlcv_bucket(row_timestamp, price, volume, input_str)
        # key_dict = data_dict.data_list.get(key)
        # key_dict[1].append(input_str)
        #
        # if price > key_dict[0][0]:
        #     key_dict[0][0] = price
        # if price < key_dict[0][1]:
        #     key_dict[0][1] = price
        # key_dict[0][2] += volume
        price_window.append(price_outlier_calculator)
        seen_keys.add(row_timestamp)
        duplicates[input_str[0]] = [input_str]
        # print(input_str)
    duplicates = {key: value for key, value in duplicates.items() if len(value) > 1}
    # for i in duplicates:
    #     for j in i:
    #
