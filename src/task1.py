import os
import csv
from datetime import datetime
from queue import Queue
import re
import threading


path = "../data"
# path = "/Users/danielyang/Desktop/sw-challenge-spring-2025/data"
file_list = os.listdir(path)
# print(file_list)

    # def __init__(self):

class DataDictionary:
    data_list = {}
    error_list = []
    queue = Queue()


def validation(input_str, error_list):
    pattern = "^([1-9]\d*(\.\d+)?),([1-9]\d*)$"
    match = re.match(pattern, input_str)
    generalized = re.sub(r"-?\d+(\.\d+)?", r"\\d+(\\.\\d+)?", input_str)
    if bool(match) is False:
        # # print(input_str)
        # regex_pattern = re.escape(input_str)
        # for i in error_list:
        #     if re.match(i[0], generalized):
        #         i.append(input_str)
        #         return False
        # new_pattern = [generalized]
        # error_list.append(new_pattern)
        # error_list[0].append(input_str)
        error_list.append(input_str)
        return False
    return True
def day_tick(files, data_list, error_list):
    for i in files:
        with open(f"/Users/danielyang/Desktop/sw-challenge-spring-2025/data/{i}", newline='') as tick:
            csv_reader = csv.reader(tick)
            entries = []
            try:
                next(csv_reader)
                first_entry = next(csv_reader)
                label = first_entry[0]
                label_timestamp = datetime.strptime(label, "%Y-%m-%d %H:%M:%S.%f")
                first_entry[0] = label_timestamp.strftime("%S.%f")
                entries.append(first_entry)
            except StopIteration:
                print(f"time error! {label_timestamp}")
                continue
            # print(label)
            for rows in csv_reader:
                try:
                    row_timestamp = datetime.strptime(rows[0], "%Y-%m-%d %H:%M:%S.%f")
                    time_validator = int(label_timestamp.strftime("%H%M%S"))
                    if time_validator > 163000 or time_validator < 93000 :
                        # print(label_timestamp.strftime("%H%M%S"))
                        # print("market closes at 4:30 PM!")
                        error_list.append(rows)
                        continue
                except ValueError:
                    # print(f"time error! {rows}")
                    continue
                full_entry = ','.join(rows[1:])
                if validation(full_entry, error_list) is False:
                    continue
                # rows[0] = row_timestamp.strftime("%f")
                key = row_timestamp.strftime("%Y%m%d%H%M%S")
                if key not in data_list.keys():
                    data_list[key] = []
                data_list.get(key).append(rows)
            # print(error_list)


def thread_manager(files, data_list, error_list):
    # thread_count = int(input("Please type how many threads you want to simultaneously run\n"))
    thread_count = 4

    # Calculate the size of each thread's slice of data
    slice_size = len(files) // thread_count

    threads = []

    # Loop to create and start threads
    for i in range(thread_count):
        # Calculate start and end indices for this thread's slice
        start_index = i * slice_size
        # Ensure the last thread gets all remaining items
        end_index = (i + 1) * slice_size if i < thread_count - 1 else len(data_list)
        # Pass the correct slice to the thread by passing a list of arguments
        thread = threading.Thread(target=day_tick, args=(files[start_index:end_index], data_list, error_list))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All threads finished.")


from datetime import datetime


def interface(interval, start_time, end_time, DataDictionary):
    # print(DataDictionary.data_list)
    print("Starting interface!")

    start_time_conversion = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time_conversion = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    end_time = int(end_time_conversion.strftime("%Y%m%d%H%M%S"))
    start_time = int(start_time_conversion.strftime("%Y%m%d%H%M%S"))

    if interval[-1] == 'h':
        format = 10000
        carry_on = 240000
    elif interval[-1] == 'm':
        format = 100
        carry_on = 6000
    elif interval[-1] == 's':
        format = 1
        carry_on = 60
    elif interval[-1] == 'd':
        format = 1000000
        carry_on = 30000000
    else:
        return "Invalid interval!"

    print(f"Start: {start_time}, End: {end_time}, Step: {format}")

    while start_time <= end_time:
        data_entry = DataDictionary.data_list.get(str(start_time))
        if data_entry is None:
            print(f"No data found for {start_time}")
        else:
            print(data_entry[0])
        start_time += format
        # Handle carry over properly
        start_time_str = str(start_time)
        masked_int = int(start_time_str[-len(str(carry_on)):])  # Extract last part
        if masked_int >= carry_on:
            new_str = start_time_str[:-len(str(carry_on))] + str(masked_int - carry_on).zfill(len(str(carry_on)))
            start_time = int(new_str)

    print("Done!")

    #write to csv based on etc factors

# print(index)
ctg_ticks = DataDictionary()
# day_tick(file_list, ctg_ticks.data_list)

# print("\n\n")
thread_manager(file_list, ctg_ticks.data_list, ctg_ticks.error_list)

# print(ctg_ticks.data_list)
print(len(ctg_ticks.data_list))
print(len(file_list))
print(ctg_ticks.data_list.get('202409160930'))
print(ctg_ticks.data_list.get('202409161456'))
print("\n\n\n")
# print(f" the errors: {ctg_ticks.error_list}")
# print(ctg_ticks.data_list)
print(ctg_ticks.data_list.get('20240916093000'))
interface('1s', '2024-09-17 12:34:01', '2024-09-20 13:33:18', ctg_ticks)