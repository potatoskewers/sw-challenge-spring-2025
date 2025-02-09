import os
import csv
import queue
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.task2 import data_clean
from src.task2 import data_queue



path = "../data"
file_list = os.listdir(path)
pattern = re.compile(r"ctg_tick_(\d{8})_(\d{4})_")
file_list.sort(key=lambda x: tuple(map(int, pattern.search(x).groups()))) #sorting file_list helps with future outlier calculations

def process_data(file):
    with open(f"{path}/{file}", newline='') as tick:
        data = list(csv.reader(tick))[1:]  # Skip header immediately
    for rows in data:
        data_queue.put(rows) #load tick into queue




class DataDictionary:
    def __init__(self):
        self.data_list = {} #initialize the dictionary to be used
        self.error_list = {}
        self.files = file_list

    def thread_manager(self, files):
        data_dicts = []
        with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as exe:  # set threads for data loading
            futures = []
            for file_name in files:
                # futures.append(exe.submit(process_data, file_name))  # run thread
                ctg = DataDictionary()
                data_dicts.append(ctg)
                futures.append(exe.submit(self.data_driver, file_name, ctg))
        for future in as_completed(futures):
             future.result()
        print("All threads finished.")
        for ctg in data_dicts:
            self.merge(ctg)
    def merge(self, other_dict):
        # Merges the current dictionary with another
        self.data_list.update(other_dict.data_list)
    def data_driver(self, file, ctg):
        process_data(file)
        data_clean(ctg)