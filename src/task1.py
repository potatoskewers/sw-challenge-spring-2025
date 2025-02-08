import os
import csv
import queue
import re
from concurrent.futures import ThreadPoolExecutor

data_queue = queue.Queue()

path = "../data"
file_list = os.listdir(path)
pattern = re.compile(r"ctg_tick_(\d{8})_(\d{4})_")
file_list.sort(key=lambda x: tuple(map(int, pattern.search(x).groups())))


class DataDictionary:
    data_list = {}
    error_list = []

def process_data(file):
    with open(f"{path}/{file}", newline='') as tick:
        data = list(csv.reader(tick))[1:]  # Skip header immediately
    for rows in data:
        data_queue.put(rows)

def thread_manager(files, data_dict):
    i = 0
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as exe:
        for file_name in files:
            exe.submit(process_data, (file_name))
            i += 1
            print(i)
    # Wait for all threads to finish
    print("All threads finished.")