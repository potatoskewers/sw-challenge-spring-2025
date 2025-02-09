from datetime import datetime

from src.task1 import DataDictionary
from src.task2 import file_list
from src.task3 import interface

if __name__ == "__main__":
    path = "../"
    driver = True
    ctg_ticks = DataDictionary() #create new dictionary to store data
    ctg_ticks.thread_manager() #begin loading process
    #sample interface runs
    interface('1s', datetime.strptime('2024-09-17 12:34:01', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-20 13:33:18', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('1d 1h 1m', datetime.strptime('2024-09-18 14:30:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-20 10:07:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('1d 1h 1m', datetime.strptime('2024-09-16 10:00:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-18 14:30:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('1d 5m 30s', datetime.strptime('2024-09-17 09:00:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-19 17:45:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('1h 15m 1m', datetime.strptime('2024-09-16 13:00:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-18 16:30:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('5d 1h 30m', datetime.strptime('2024-09-16 11:30:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-20 18:00:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('30m 5m 1m', datetime.strptime('2024-09-17 15:20:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-19 19:00:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    interface('1d 10m 2m', datetime.strptime('2024-09-16 12:00:00', "%Y-%m-%d %H:%M:%S"),
              datetime.strptime('2024-09-19 22:30:00', "%Y-%m-%d %H:%M:%S"), ctg_ticks)
    while True:
        print("the interval is in the format of 'xs', 'xm', 'xh', 'xd', etc and can support combinations in the format of 'xs,xm,xh,xd' where x is any positive integer")
        print("the start and end time must be in the format of 'Y-m-d H:M:S'")
        input_str = input("Please input the ohlcv file you want to generate in the format of \"interval,start time,end time\"\n")
        if input_str == "quit":
            break
        values = input_str.split(',') #process each input
        interval = values[0]
        start_time = values[1]
        end_time = values[2]
        if interval is None or start_time is None or end_time is None: #handle bad input
            print("invalid input")
        else:
            interface(interval, datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"), datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"), ctg_ticks)


