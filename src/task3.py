import csv
import os
from datetime import datetime, timedelta

def interface(interval, start_time, end_time, ctg):
    print("Generating File!")
    #process the interval
    times = interval.split(" ")
    time_frame = 0
    for i in times: #convert interval into seconds to determine end-time for each interval
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
    format_start_time = start_time.strftime("%Y%m%d%H%M%S") #format times for file name generation
    format_end_time = end_time.strftime("%Y%m%d%H%M%S")
    file_path = f'../generated-ohlcv-csvs/ctg_{"".join(times)}_{format_start_time}_{format_end_time}ohlcv.csv'
    with open(file_path, 'w', newline='') as csvfile:
        current_time = start_time #set pointer to start_time
        fields = ['Timestamp', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume'] #define dataset fields
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        while current_time < end_time:
            end_interval = current_time + timedelta(seconds = time_frame) #set the time for the end of interval
            open_price = ctg.data_list.get(current_time) #check if open_price exists
            close_price = ctg.data_list.get(end_interval) #check if close_price exists
            if open_price is not None:
                 open_price = ctg.data_list.get(current_time).open_price #open_price is price at current_time
            else:
                 current_time += timedelta(seconds=1) #adjust interval to next second and try again
                 continue
            if close_price is not None:
                 close_price = ctg.data_list.get(end_interval).close_price #close_price is price at end_interval
            else:
                 current_time += timedelta(seconds=1) #adjust interval to next second and try again
                 continue
            high_price = 0 #initialize high_price for interval
            low_price = 99999999999999999999999999999 #initialize low_price for interval
            volume = 0 #initialize volume for interval
            start_time = current_time #set the start of the interval to be the current_time
            while current_time <= end_interval:
                if current_time.hour >= 16 and current_time.minute >= 30: #skip if after-market hours
                     current_time = current_time.replace(hour=9, minute=30) + timedelta(days=1)
                data_entry = ctg.data_list.get(current_time) #obtain DataBucket with ohlcv values for the second
                if data_entry is not None:
                    if data_entry.high_price > high_price: #set high_price if the data_entry's high price is higher
                        high_price = data_entry.high_price
                    if data_entry.low_price < low_price: #set low_price if the data_entry's low price is lower
                        low_price = data_entry.low_price
                    volume += data_entry.volume #add volume to total in interval
                current_time += timedelta(seconds=1) #move to next second
            # write to file
            writer.writerow({
                'Timestamp' : start_time,
                'Open Price': open_price,
                'High Price': high_price,
                'Low Price': low_price,
                'Close Price': close_price,
                'Volume': volume
            })
    print(f"OHLCV csv file generated at path {os.path.abspath(file_path)}\n\n")