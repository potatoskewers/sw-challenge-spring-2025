import os
import csv


path = "/Users/danielyang/Desktop/sw-challenge-spring-2025/data"
file_list = os.listdir(path)
# print(file_list)


def day_tick(files):
    index = {}
    for i in files:
        with open(f"/Users/danielyang/Desktop/sw-challenge-spring-2025/data/{i}", newline='') as tick:
            csv_reader = csv.reader(tick)
            entries = []
            next(csv_reader)
            entries.append(next(csv_reader))
            label = entries[0][0]
            #print(label)
            for rows in csv_reader:
                entries.append(rows)
            #print(f"{label[0:4]}{label[5:7]}{label[8:10]}{label[11:13]}{label[14:16]}")
            index[f"{label[0:4]}{label[5:7]}{label[8:10]}{label[11:13]}{label[14:16]}"] = entries
    #print(index)
    return index


file_tracker = day_tick(file_list)
# print(file_tracker)

