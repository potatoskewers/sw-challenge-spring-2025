import heapq
import os
import csv
import queue
from datetime import datetime, timedelta
import re
import statistics
from concurrent.futures import ThreadPoolExecutor

path = "../data"
file_list = os.listdir(path)
pattern = re.compile(r"ctg_tick_(\d{8})_(\d{4})_")
file_list.sort(key=lambda x: tuple(map(int, pattern.search(x).groups())))

data_queue = queue.Queue()

class DataDictionary:
    data_list = {}
    error_list = []

def validation(data_dict):
    price_upper_bound = 9999999999999999999999999999999
    price_lower_bound = 0
    volume_lower_bound = 100
    price_outlier_flag = []
    duplicates = {}
    seen_keys = set()
    price_window = [float(data_queue.queue[0][1])]
    volume_window = [int(data_queue.queue[0][2])]
    volume_outlier_window = data_queue.qsize()*.03
    i = 0
    pattern = re.compile(r"^([1-9]\d*(\.\d+)?),([1-9]\d*)$")
    price_outlier_window = (data_queue.qsize())*.10
    while not data_queue.empty():
        i += 1
        input_str = data_queue.get()
        try:
            row_timestamp = datetime.strptime(input_str[0], "%Y-%m-%d %H:%M:%S.%f")
            # time_validator = int(row_timestamp.strftime("%H%M%S"))
            # if time_validator > 163000 or time_validator < 93000:
                # print(label_timestamp.strftime("%H%M%S"))
                # print("market closes at 4:30 PM!")
                # data_dict.error_list.append(input_str)
        except ValueError:
            print(f"time error!")
            continue
        full_entry = ','.join(input_str[1:])
        if not pattern.match(full_entry):
            # print("match false!")
            continue
        # rows[0] = row_timestamp.strftime("%f")
        price_outlier_calculator = float(input_str[1])
        volume_outlier_calculator = int(input_str[2])
        if len(price_window) > price_outlier_window:
            price_window.pop(0)
        if volume_outlier_calculator < volume_lower_bound:
            # print(f"cleaned low volume:{volume_outlier_calculator} under {volume_lower_bound}")
            continue
        if i > price_outlier_window:  # Ensure enough data points
            i = 0  # Reset counter
            price_q1 = statistics.quantiles(price_window, n=4)[0]
            price_q3 = statistics.quantiles(price_window, n=4)[2]
            IQR = price_q3 - price_q1
            price_lower_bound = price_q1 - 5 * IQR
            price_upper_bound = price_q3 + 5 * IQR
        if price_outlier_calculator < price_lower_bound or price_outlier_calculator > price_upper_bound:
            price_outlier_flag.append(input_str)
            print(f"Outlier detected! {input_str} with bounds {price_lower_bound} and {price_upper_bound}")
            continue  # Skip adding this outlier value
            # Append only valid numbers
        key = row_timestamp.strftime("%Y%m%d%H%M%S")
        if input_str[0] in seen_keys:
            # print(f"duplicate value found: {input_str}")
            if input_str[0] not in duplicates:
                duplicates[input_str[0]] = []
            duplicates[input_str[0]].append(input_str)
            continue
        elif key not in data_dict.data_list.keys():
            data_dict.data_list[key] = []
        data_dict.data_list.get(key).append(input_str)
        price_window.append(price_outlier_calculator)
        seen_keys.add(input_str[0])
        duplicates[input_str[0]] = [input_str]
        volume_window.append(volume_outlier_calculator)
    duplicates = {key: value for key, value in duplicates.items() if len(value) > 1}

def process_data(file):
    with open(f"{path}/{file}", newline='') as tick:
        data = list(csv.reader(tick))[1:]  # Skip header immediately
    for rows in data:
        data_queue.put(rows)

def thread_manager(files, data_dict):
    # thread_count = int(input("Please type how many threads you want to simultaneously run\n"))

    # Calculate the size of each thread's slice of data

    threads = []
    i = 0
    # for file_name in files:
    #     try:
    #         thread = threading.Thread(target=process_data, args=(file_name,))
    #         threads.append(thread)
    #         thread.start()
    #         i += 1
    #         print(i)
    #     except RuntimeError:
    #         print("err")

    i = 0
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as exe:
        for file_name in files:
            exe.submit(process_data, (file_name))
            i += 1
            print(i)
    # Wait for all threads to finish
    print("All threads finished.")
    validation(data_dict)

def interface(interval, start_time, end_time, ctg):
    print("Starting interface!")
    start_time_conversion = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time_conversion = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    times = interval.split(",")
    time_frame = 0
    for i in times:
        if i[-1] == 'h':
            time_frame += int(i[:-1]) * 3600
        elif i[-1] == 'm':
            time_frame += int(i[:-1]) * 60
        elif i[-1] == 's':
            time_frame += int(i[:-1]) * 1
        elif i[-1] == 'd':
            time_frame += int(i[:-1]) * 86400
        else:
            return "Invalid interval!"
    with open(f'../ctg_{"".join(times)}_{start_time}_{end_time}ohlcv.csv', 'w', newline='') as csvfile:
        current_time = start_time_conversion
        fields = ['Timestamp', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        current_time_int = int(start_time_conversion.strftime("%Y%m%d%H%M%S"))
        end_int = int(end_time_conversion.strftime("%Y%m%d%H%M%S"))
        while current_time_int < end_int:
            end_interval = current_time + timedelta(seconds = time_frame)
            end_interval_conversion = end_interval.strftime("%Y%m%d%H%M%S")
            end_interval_int = int(end_interval_conversion)
            open_price = ctg.data_list.get(current_time.strftime("%Y%m%d%H%M%S"))
            close_price = ctg.data_list.get(end_interval_conversion)
            if open_price is not None:
                open_price = open_price[0][1]
            else:
                print(f"open price not found! for a key of {current_time.strftime('%Y%m%d%H%M%S')}")
                current_time += timedelta(seconds=1)
                current_time_int = int(current_time.strftime("%Y%m%d%H%M%S"))
                continue
            if close_price is not None:
                close_price = close_price[0][1]
            else:
                print(f"close price not found! for a key of {end_interval_conversion}")
                current_time += timedelta(seconds=1)
                current_time_int = int(current_time.strftime("%Y%m%d%H%M%S"))
                continue
            high_price = 0
            low_price = 99999999999999999999999999999
            volume = 0
            start_time = current_time
            while current_time_int <= end_interval_int:
                if current_time.hour == 23 and current_time.minute >= 59:
                    current_time = current_time.replace(hour=9, minute=30) + timedelta(days=1)
                data_entry = ctg.data_list.get(current_time.strftime('%Y%m%d%H%M%S'))
                if data_entry is None:
                    print(f"No data found for {current_time.strftime('%Y-%m-%d %H:%M:%S')} with key {current_time.strftime('%Y%m%d%H%M%S')}")
                else:
                    for i in data_entry:
                        price_float = float(i[1])
                        volume += int(i[2])
                        if price_float > high_price:
                            high_price = price_float
                        if price_float < low_price:
                            low_price = price_float
                current_time += timedelta(seconds=1)
                #write to csv based on etc factors
                current_time_int = int(current_time.strftime("%Y%m%d%H%M%S"))
            writer.writerow({
                'Timestamp' : start_time,
                'Open Price': open_price,
                'High Price': high_price,
                'Low Price': low_price,
                'Close Price': close_price,
                'Volume': volume
            })


# print(index)
ctg_ticks = DataDictionary()
# day_tick(file_list, ctg_ticks.data_list)

# print("\n\n")
thread_manager(file_list, ctg_ticks)
# print(ctg_ticks.data_list)
print(len(ctg_ticks.data_list))
print(len(file_list))
print("\n\n\n")
# print(f" the errors: {ctg_ticks.error_list}")
# print(ctg_ticks.data_list)
print(ctg_ticks.data_list.get('20240916093000'))
print(ctg_ticks.data_list)
interface('1s', '2024-09-17 12:34:01', '2024-09-20 13:33:18', ctg_ticks)
interface('1d,1h,1m', '2024-09-18 14:30:00', '2024-09-20 10:07:00', ctg_ticks)
# print(data_queue.qsize())
# # print(ctg_ticks.data_list)
# print(len(ctg_ticks.error_list))
