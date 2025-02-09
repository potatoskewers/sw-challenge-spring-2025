import queue
import statistics
from datetime import datetime, timedelta

data_queue = queue.Queue()

class DataBucket:
    #each bucket belongs to each second that a trade(s) occurred
    def __init__(self, first_time):
        self.rows = [] #ticks that happened within the second
        self.open_time = first_time + timedelta(seconds=1) #initialize time of first trade in the second
        self.close_time = first_time #initialize time of last trade in the second
        self.open_price = None
        self.close_price = None
        self.high_price = 0
        self.low_price = 999999999999999999999999
        self.volume =  0
    def ohlcv_bucket(self, curr_time, price, volume, row):
        if curr_time < self.open_time:
            self.open_time = curr_time #open_time to current time if current time is earlier than open_time
            self.open_price = price #set open_price to current price
        if curr_time > self.close_time:
            self.close_time = curr_time #set close_time to current_time if current_time later than close_time
            self.close_price = price #set close_price to current price
        if price > self.high_price:
            self.high_price = price #price to the highest price if price more than high price
        if price < self.low_price:
            self.low_price = price #price to the lowest price if price less than high price
        self.volume += volume #add to total volume in the second
        self.rows.append(row) #add tick to raw data

def data_clean(data_dict):
    price_upper_bound = 500 #instantiated temporary bounds
    price_lower_bound = 400
    volume_lower_bound = 10
    duplicates = {}
    seen_keys = set()
    market_open_hour = 9 # calculate only market hours since after hours have too little liquidity
    market_open_minute = 30
    market_close_hour = 16
    market_close_minute = 30
    i = 0
    j = True
    price_outlier_window = (data_queue.qsize())*.10
    while not data_queue.empty():
        i += 1
        input_str = data_queue.get() #pop off from queue
        try:
            row_timestamp = datetime.strptime(input_str[0], "%Y-%m-%d %H:%M:%S.%f")
            #set the key for the dictionary entry
            key = row_timestamp.replace(microsecond=0)
        except ValueError:
            print(f"time error!")
            continue
        # skip data that has invalid timestamp
        hour = row_timestamp.hour
        minute = row_timestamp.minute
        #skip data that is before trading hours or after trading hours
        if hour > market_close_hour and minute > market_close_minute or hour < market_open_hour and minute < market_open_minute:
            continue
        price_str = input_str[1].strip() if input_str[1] else None
        volume_str = input_str[2].strip() if input_str[2] else None
        # skip if any of the fields are None or empty
        if not price_str or not volume_str:
            continue
        price = float(price_str) #obtain price from the tick
        volume = int(volume_str) #obtain volume from the tick
        #adjust the window to calculate price outliers
        if j is True:
            price_window = [input_str[1]]# window to calculate
        #check if the time is valid
        if len(price_window) > price_outlier_window:
            price_window.pop(0)
        #calculate a new reasonable outlier bound every (price_outlier_window) ticks
        if i >= price_outlier_window:
            i = 0
            price_q1 = statistics.quantiles(price_window, n=4)[0]
            price_q3 = statistics.quantiles(price_window, n=4)[2]
            price_iqr = price_q3 - price_q1
            price_lower_bound = price_q1 - 5 * price_iqr
            price_upper_bound = price_q3 + 5 * price_iqr
        #skip insignificant volumes as it adds noise to dataset
        if volume < volume_lower_bound:
            continue
        #skip outlier errors
        if price < price_lower_bound or price > price_upper_bound:
            continue
        #append duplicate timestamps to be aggregated for later
        if row_timestamp in seen_keys:
            if row_timestamp not in duplicates:
                duplicates[row_timestamp] = [row_timestamp, float(input_str[1]), int(input_str[2]), 1]
            else:
                dupe_count = duplicates.get(row_timestamp)[3]
                curr_avg =duplicates.get(row_timestamp)[1]
                duplicates.get(row_timestamp)[1] = (price + curr_avg*dupe_count) / (dupe_count + 1) #calculate average of the duplicates to be used for data
                duplicates.get(row_timestamp)[2] += volume #calculate total volume to be used for data
                duplicates.get(row_timestamp)[3] += 1
            continue
        elif key not in data_dict.data_list.keys():
            data_dict.data_list[key] = DataBucket(key) #create DataBucket
        data_dict.data_list.get(key).ohlcv_bucket(row_timestamp, price, volume, input_str) #evaluate ohlcv for interval of the second
        price_window.append(price) #insert price to the outlier window
        seen_keys.add(row_timestamp) #add current time to keys seen
        duplicates[row_timestamp] = [row_timestamp, price, volume, 1] #intialize
        # print(input_str)
        j = False
    duplicates = {key: value for key, value in duplicates.items() if value[3] == 1} #filter out values that found no duplicates

    #aggregate the duplicate values
    for i in duplicates:
        timestamp = i.replace(microsecond=0) #generate key
        print(timestamp)
        index = next((j for j, item in enumerate(data_dict.data_list.get(timestamp).rows) if item[0] == i), None) #find index for time that matches i
        if index is not None:
            rows = data_dict.data_list.get(timestamp).rows
            values = duplicates.get(i)
            rows[index] = [i, values[1], values[2]] #change that entry to the duplicates entry
            data_dict.data_list[i] = DataBucket(i) #recalculate ohlcv values by resetting DataBucket
            for k in rows:
                data_dict.data_list.get(timestamp).ohlcv_bucket(k[0], k[1], k[2], k) #recalculate ohlcv values with new aggregated duplicate
    print("Data Cleaning Complete!")
