import os
import queue
import statistics
from datetime import datetime, timedelta
import re

path = "../data"
file_list = os.listdir(path)
pattern = re.compile(r"ctg_tick_(\d{8})_(\d{4})_")
file_list.sort(key=lambda x: tuple(map(int, pattern.search(x).groups()))) #sorting file_list helps with future outlier calculations

data_queue = queue.Queue()
file_queue = queue.Queue()
for i in file_list:
    file_queue.put(i)

class DataBucket:
    #each bucket belongs to each second that a trade(s) occurred
    def __init__(self, first_time):
        self.rows = [] #ticks that happened within the second
        self.open_time = first_time + timedelta(seconds=1) #initialize time of first trade in the second
        self.close_time = first_time #initialize time of last trade in the second
        self.open_price = None #initialize vlaues
        self.close_price = None
        self.high_price = None
        self.low_price = None
        self.volume =  0

    def ohlcv_bucket(self, curr_time, price, volume, row):
        if curr_time <= self.open_time:
            self.open_time = curr_time #open_time to current time if current time is earlier than open_time
            self.open_price = price #set open_price to current price
        if curr_time >= self.close_time:
            self.close_time = curr_time #set close_time to current_time if current_time later than close_time
            self.close_price = price #set close_price to current price
        if self.high_price is None or price > self.high_price:
            self.high_price = price #price to the highest price if price more than high price
        if self.low_price is None or price < self.low_price:
            self.low_price = price #price to the lowest price if price less than high price
        self.volume += volume #add to total volume in the second
        self.rows.append(row) #add tick to raw data
    def merge(self, bucket):
        for i in bucket.rows:
            self.ohlcv_bucket(i[0], i[1], i[2], i)

def data_clean(data_dict):
    while True:
        try:
            rows = data_queue.get(timeout=2)
        except queue.Empty:
            break
        volume_lower_bound = 10
        duplicates = {}
        seen_keys = set()
        prices = []
        for row in rows: #obtain prices for outlier calculations
            try:
                prices.append(float(row[1]))
            except ValueError:
                continue
        sorted_prices = sorted(prices)
        n = len(sorted_prices)

        # Calculate Q1 (25th percentile) and Q3 (75th percentile)
        Q1 = sorted_prices[n // 4]  # Approximate Q1
        Q3 = sorted_prices[(3 * n) // 4]  # Approximate Q3
        IQR = Q3 - Q1

        price_lower_bound = Q1 - 5 * IQR
        price_upper_bound = Q3 + 5 * IQR
        for row in rows:
            input_str = row #pop off from queue
            try:
                row_timestamp = datetime.strptime(input_str[0], "%Y-%m-%d %H:%M:%S.%f")
                #set the key for the dictionary entry
                key = row_timestamp.replace(microsecond=0)
            except ValueError:
                continue
            # skip data that has invalid timestamp
            hour = row_timestamp.hour
            minute = row_timestamp.minute
            combined_time = int(f"{row_timestamp.hour:02d}{row_timestamp.minute:02d}")
            #skip data that is before trading hours or after trading hours
            if combined_time < 930 or combined_time > 1630:
                continue
            price_str = input_str[1].strip() if input_str[1] else None
            volume_str = input_str[2].strip() if input_str[2] else None
            # skip if any of the fields are None or empty
            if not price_str or not volume_str:
                continue
            price = float(price_str) #obtain price from the tick
            volume = int(volume_str) #obtain volume from the tick
            #adjust the window to calculate price outliers
            if price < 0:
                continue
            #check if the time is valid
            # if volume < 0: #check for negative volume
            #     continue
            # if volume == 0: #check for empty volumes
            #     continue
            if volume < volume_lower_bound:
                continue
            #skip outlier errors
            if price < price_lower_bound or price > price_upper_bound:
                continue
            #append duplicate timestamps to be aggregated for later
            if row_timestamp in seen_keys:
                if input_str in data_dict.data_list.get(key).rows: #check for any duplicate entries
                    #print(f"duplicate entry found! {input_str}")
                    continue
                else:
                    dupe_count = duplicates.get(row_timestamp)[3]
                    curr_avg =duplicates.get(row_timestamp)[1]
                    duplicates.get(row_timestamp)[1] = (price + curr_avg*dupe_count) / (dupe_count + 1) #calculate average of the duplicates to be used for data
                    duplicates.get(row_timestamp)[2] += volume #calculate total volume to be used for data
                    duplicates.get(row_timestamp)[3] += 1
                    data_dict.data_list.get(key).ohlcv_bucket(row_timestamp, duplicates.get(row_timestamp)[1], volume, input_str) #handle duplicates in ohlcv calculation
                continue
            elif key not in data_dict.data_list.keys():
                data_dict.data_list[key] = DataBucket(key) #create DataBucket
            data_dict.data_list.get(key).ohlcv_bucket(row_timestamp, price, volume, input_str) #evaluate ohlcv for interval of the second
            # price_window.append(price) #insert price to the outlier window
            seen_keys.add(row_timestamp) #add current time to keys seen
            duplicates[row_timestamp] = [row_timestamp, price, volume, 1] #intialize
