import csv
from datetime import datetime, timedelta



def interface(interval, start_time, end_time, ctg):
    print("Starting interface!")
    start_time_conversion = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time_conversion = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    times = interval.split(",")
    time_frame = 0
    for i in times:
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
    with open(f'../ctg_{"".join(times)}_{start_time}_{end_time}ohlcv.csv', 'w', newline='') as csvfile:
        current_time = start_time_conversion
        fields = ['Timestamp', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        while current_time < end_time_conversion:
            end_interval = current_time + timedelta(seconds = time_frame)
            # end_interval_conversion = end_interval.strftime("%Y%m%d%H%M%S")
            # end_interval_int = int(end_interval_conversion)
            # open_price = ctg.data_list.get(current_time.strftime("%Y%m%d%H%M%S"))
            # close_price = ctg.data_list.get(end_interval_conversion)
            open_price = ctg.data_list.get(current_time)
            close_price = ctg.data_list.get(end_interval)
            if open_price is not None:
                 open_price = ctg.data_list.get(current_time).open_price
            else:
                 print(f"open price not found! for a key of {current_time.strftime('%Y%m%d%H%M%S')}")
                 current_time += timedelta(seconds=1)
            #     current_time_int = int(current_time.strftime("%Y%m%d%H%M%S"))
                 continue
            if close_price is not None:
                 close_price = ctg.data_list.get(end_interval).close_price
            else:
                 print(f"close price not found! for a key of {end_interval}")
                 current_time += timedelta(seconds=1)
            #     current_time_int = int(current_time.strftime("%Y%m%d%H%M%S"))
                 continue
            high_price = 0
            low_price = 99999999999999999999999999999
            volume = 0
            start_time = current_time
            while current_time <= end_interval:
                if current_time.hour >= 16 and current_time.minute >= 30:
                    current_time = current_time.replace(hour=9, minute=30) + timedelta(days=1)
                data_entry = ctg.data_list.get(current_time)
                if data_entry is None:
                    print(f"No data found for {current_time.strftime('%Y-%m-%d %H:%M:%S')} with key {current_time}")
                else:
                    # data_high_price = data_entry[0][0]
                    # data_low_price = data_entry[0][1]
                    # data_volume = data_entry[0][2]
                    # if data_high_price > high_price:
                    #     high_price = data_high_price
                    # if data_low_price < low_price:
                    #     low_price = data_low_price
                    # volume += data_volume
                    # for i in data_entry:
                    #     price_float = float(i[1])
                    #     volume += int(i[2])
                    #     if price_float > high_price:
                    #         high_price = price_float
                    #     if price_float < low_price:
                    #         low_price = price_float
                    if data_entry.high_price > high_price:
                        high_price = data_entry.high_price
                    if data_entry.low_price < low_price:
                        low_price = data_entry.low_price
                    volume += data_entry.volume
                current_time += timedelta(seconds=1)
                #write to csv based on etc factors
                # current_time_int = int(current_time.strftime("%Y%m%d%H%M%S"))
            writer.writerow({
                'Timestamp' : start_time,
                'Open Price': open_price,
                'High Price': high_price,
                'Low Price': low_price,
                'Close Price': close_price,
                'Volume': volume
            })