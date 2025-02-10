import concurrent
import os
import csv
import queue
import re
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import time, timedelta
import time

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
        start_time = time.time()
        max_workers = os.cpu_count() * 1
        data_cleaners = int(max_workers * 0.2)
        data_loaders = max_workers - data_cleaners
        data_dicts = []
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as exe:  # set threads for data loading
            for i in range(data_loaders):
                futures.append(exe.submit(process_data))
            for i in range(data_cleaners):
                ctg = DataDictionary()
                data_dicts.append(ctg)
                futures.append(exe.submit(data_clean, ctg))
        for future in concurrent.futures.as_completed(futures):
            future.result()
        print("All threads finished. Data is ready to be used.")
        for ctg in data_dicts:
            self.merge(ctg)
        end_time = time.time()
        print(f"total loading time = {end_time - start_time}")


    def merge(self, other_dict):
        for key, bucket in other_dict.data_list.items():
            if key in self.data_list:
                # Combine bucket data instead of overwriting
                print("overlap detected!")
                self.data_list[key].merge(bucket)
            else:
                self.data_list[key] = bucket # if no duplicate