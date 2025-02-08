from src.task1 import DataDictionary, thread_manager, file_list
from src.task2 import data_clean
from src.task3 import interface

if __name__ == "__main__":
    # print(index)
    ctg_ticks = DataDictionary()
    # day_tick(file_list, ctg_ticks.data_list)
    # print("\n\n")
    thread_manager(file_list, ctg_ticks)
    data_clean(ctg_ticks)
    # print(ctg_ticks.data_list)
    print(len(ctg_ticks.data_list))
    print(len(file_list))
    print("\n\n\n")
    # print(f" the errors: {ctg_ticks.error_list}")
    # print(ctg_ticks.data_list)
    # print(ctg_ticks.data_list)
    interface('1s', '2024-09-17 12:34:01', '2024-09-20 13:33:18', ctg_ticks)
    interface('1d,1h,1m', '2024-09-18 14:30:00', '2024-09-20 10:07:00', ctg_ticks)
    interface('1d,1h,1m', '2024-09-16 10:00:00', '2024-09-18 14:30:00', ctg_ticks)
    interface('1d,5m,30s', '2024-09-17 09:00:00', '2024-09-19 17:45:00', ctg_ticks)
    interface('1h,15m,1m', '2024-09-16 13:00:00', '2024-09-18 16:30:00', ctg_ticks)
    interface('5d,1h,30m', '2024-09-16 11:30:00', '2024-09-20 18:00:00', ctg_ticks)
    interface('30m,5m,1m', '2024-09-17 15:20:00', '2024-09-19 19:00:00', ctg_ticks)
    interface('1d,10m,2m', '2024-09-16 12:00:00', '2024-09-19 22:30:00', ctg_ticks)