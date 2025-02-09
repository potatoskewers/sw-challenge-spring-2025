import concurrent
import os
import csv
import queue
import re
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor, wait
from src.task2 import data_clean, path, file_list
from src.task2 import data_queue
from src.task2 import file_queue


def process_data():
    while not file_queue.empty():
        file = file_queue.get()
        with open(f"{path}/{file}", newline='') as tick:
            data = list(csv.reader(tick))[1:]  # Skip header immediately
        rows = []
        for row in data:
            rows.append(row)
        data_queue.put(rows) #load tick into queue

class DataDictionary:
    def __init__(self):
        self.data_list = {} #initialize the dictionary to be used
        self.error_list = {}
        self.files = file_list

    def thread_manager(self):
        max_workers = os.cpu_count() * 2 * 100
        data_loaders = int(max_workers * .8)
        data_cleaners = max_workers - data_loaders

        data_dicts = []
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as exe:  # set threads for data loading
            for i in range(data_loaders):
                futures.append(exe.submit(process_data))
            for i in range(data_cleaners):
                ctg = DataDictionary()
                data_dicts.append(ctg)
                futures.append(exe.submit(data_clean, ctg))
            # while not file_queue.empty():
            #     file = file_queue.get()
            #     ctg = DataDictionary()
            #     data_dicts.append(ctg)
            #     futures.append(exe.submit(data_clean, ctg))
        for future in concurrent.futures.as_completed(futures):
            future.result()
        print("All threads finished.")
        for ctg in data_dicts:
            self.merge(ctg)

    def merge(self, other_dict):
        for key, bucket in other_dict.data_list.items():
            if key in self.data_list:
                # Combine bucket data instead of overwriting
                print("overlap detected!")
                self.data_list[key].merge(bucket)  # Assuming `DataBucket` has a `merge` method
            else:
                self.data_list[key] = bucket
        # if not other_dict.data_list:
        #     print("empty data_list!")
        # # Merges the current dictionary with another
        # self.data_list.update(other_dict.data_list)