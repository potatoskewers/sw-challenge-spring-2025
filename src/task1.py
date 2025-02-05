import os
import csv
from datetime import datetime
import re
import threading



path = "/Users/danielyang/Desktop/sw-challenge-spring-2025/data"
file_list = os.listdir(path)
# print(file_list)

    # def __init__(self):

class DataDictionary:
    data_list = {}
    error_list = []


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
                # print(f"time error! {label_timestamp}")
                continue
            # print(label)
            for rows in csv_reader:
                try:
                    row_timestamp = datetime.strptime(rows[0], "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    continue
                full_entry = ','.join(rows[1:])
                if validation(full_entry, error_list) is False:
                    continue
                rows[0] = row_timestamp.strftime("%S.%f")
                entries.append(rows)
            data_list[label_timestamp.strftime("%Y%m%d%H%M")] = entries
            print(error_list)


def thread_manager(files, data_list, error_list):
    thread_count = int(input("Please type how many threads you want to simultaneously run\n"))

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

    # print(index)
ctg_ticks = DataDictionary()
# day_tick(file_list, ctg_ticks.data_list)

# print("\n\n")
thread_manager(file_list, ctg_ticks.data_list, ctg_ticks.error_list)

print(ctg_ticks.data_list)
print(len(ctg_ticks.data_list))
print(len(file_list))
print(ctg_ticks.data_list.get('202409160930'))
print(ctg_ticks.data_list.get('202409191641'))
print("\n\n\n")
print(f" the errors: {ctg_ticks.error_list}")
