# Data Report

### Table of Contents

1. [Data Loading](#data-loading)
2. [Data Cleaning Report](#data-cleaning-report)
3. [Errors](#errors)
4. [Discarded Data](#discarded-data)
5. [Formatted Data](#formatted-data)
6. [**Interface Preperation**](#interface-preperation)

<hr style="border: 2px solid grey;">

## Data Loading
When loading the data, I chose multithreading so that I can load multiple data files at the same time. I also made sure to load the data into a queue as queues are thread-safe, meaning that the threads will not collide when trying to store/retrieve data and possibly corrupt the data.

<hr style="border: 2px solid grey;">

### Approach:
1. First, I loaded all of the files into a queue. This way, while the files were being loaded off of a queue,
they would be eventually placed into another data queue which would be processed for cleaning.

```python
file_queue = queue.Queue()
for i in file_list:
    file_queue.put(i)
# This is in the task2.py file rather than task1
```
2. Then, I initialized threads that would continuously pop off of the queue
until there were no more files left.
```python
 with ThreadPoolExecutor(max_workers=max_workers) as exe:  # set threads for data loading
        for i in range(data_loaders):
            futures.append(exe.submit(process_data))
        for i in range(data_cleaners):
            ctg = DataDictionary()
            data_dicts.append(ctg)
            futures.append(exe.submit(data_clean, ctg))
```
3. For each file popped off of the queue, I read all of the rows within the file,
and then put it into a list of rows to be put in the data cleaning queue.
```python
def process_data():
    while not file_queue.empty(): #process files until no more in file_queue
        file = file_queue.get()
        with open(f"{path}/{file}", newline='') as tick:
            data = list(csv.reader(tick))[1:]  # Skip header immediately
        rows = []
        for row in data:
            rows.append(row)
        data_queue.put(rows) # load collection of seconds within the minute to be cleaned
```
An important feature that I noticed about the data is that each CSV contained 
all of the seconds within the minute (e.g. the collection of data entries during 2024 09:20)
* This would help me for later outlier calculation, ohlcv calculations, data grouping,
and more. 
* These key features of the data is why i put each entry in the data cleaning queue as a 
batch of entries that occurred within a minute

<hr style="border: 2px solid grey;">

### Issues:
 * My first approach was to use one thread per file, and this turned out even slower than using less due to computational constraints and thread overloading
   * I reduced the amount of threads heavily, and tried to find the right data cleaning thread count to cpu core ratio, and with multiple runs I found that these configurations ran the fastest for me:
     ```python
      max_workers = os.cpu_count() * 1 #total workers
      data_cleaners = int(max_workers * 0.2) #total data cleaning threads
      data_loaders = max_workers - data_cleaners #total data processing threads
      ```
 * Another issue that I ran into was that while the threads were processing data, my driver method in main.py was trying to execute the interface too early before all the data loaded into memory.
   * To fix this, i researched asynchronous I/O libraries and then 
   imported the futures library and ensured that the interfaces didn't run until the data was fully loaded.
      ```python
        with ThreadPoolExecutor(max_workers=max_workers) as exe:  # set threads for data loading
            for i in range(data_loaders):
                futures.append(exe.submit(process_data))
            for i in range(data_cleaners):
                ctg = DataDictionary()
                data_dicts.append(ctg)
                futures.append(exe.submit(data_clean, ctg))
        for future in concurrent.futures.as_completed(futures):
            future.result() #iterate once thread is finished
        print("All threads finished. Data is ready to be used.")
        for ctg in data_dicts:
            self.merge(ctg) #merge all dictionaries into one dictionary
        end_time = time.time()
        print(f"total loading time = {end_time - start_time}")
      ```

<hr style="border: 2px solid grey;">


## Data Cleaning Report:
When processing the data, each tick filtered into three sections:
* **Discard**
* **Format**
* **Accepted**


For each tick entry, I checked the following criteria to make sure it was discarded, formatted, or accepted. Data that might not be appropriate for computer processing is still valid data and should still be accounted for, but data that is clearly invalid or irrelevant should be deleted.

<hr style="border: 2px solid grey;">

### Errors

The four common errors I found:  
1. missing prices
2. missing volume
3. negative price
4. extreme outliers

**Missing Prices:**

I detected multiple instances where prices were missing, and these prices can’t be assumed so they were immediately discarded.

```python
price_str = input_str[1].strip() if input_str[1] else None
```

**Missing Volume:**

Same with the prices, these volumes cannot be assumed, so they are immediately discarded.

```python
volume_str = input_str[2].strip() if input_str[2] else None
```

**Negative prices:**

Under the assumption that the prices without the negative sign is not valid, these data points were immediately discarded since they were corrupted.
These negative errors happened frequently, but didn’t make up a majority of the data, which is why I also applied this reasoning.

```python
price = float(price_str
if price < 0:
    continue

```

**Extreme Outliers**
Outliers in the top/bottom 0.05% of the general median trend have seemingly impossible values, discarding them immediately.
```python
sorted_prices = sorted(prices)
    n = len(sorted_prices)

    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = sorted_prices[n // 4]  # Approximate Q1
    Q3 = sorted_prices[(3 * n) // 4]  # Approximate Q3
    IQR = Q3 - Q1

    price_lower_bound = Q1 - 5 * IQR
    price_upper_bound = Q3 + 5 * IQR
```

<hr style="border: 2px solid grey;">

### Discarded Data:
This data has features that make the data unusable, since the features make the data unreadable, seem impossible with the rest of our data
or is valid but has characteristics that make the data irrelevant to our analysis. 

**Low Volume:**

While not errors, I considered low-volume purchases to be under 10 and discarded these immediately
These transactions are fractional and noisy, masking important trends in the tick data.

```python
    volume_lower_bound = 10
    if volume < volume_lower_bound:
         continue
```

**Market after hours tick data:**

While not errors, due to the lower liquidity of after hours tick data, I assumed this data as negligible and discarded the after hours tick data.

```python
combined_time = int(f"{row_timestamp.hour:02d}{row_timestamp.minute:02d}")
            #skip data that is before trading hours or after trading hours
            if combined_time < 930 or combined_time > 1630:
                continue
```

**Outliers:**

While not errors, these are noise that don’t tell much about the generalized pattern that the tick data holds and should be discarded.
However, I couldn’t figure out a way to properly dispose of outliers in the fourth quartile without ruining valid data entries, so I got rid of the extreme 0.05% outliers
* I assumed the outliers to have valid formats, as there was no way to safely say the outliers had a formatting error but contain valid values (e.g. misplaced decimal)
These outliers happened frequently, but didn’t make up a majority of the data, which is why I also applied this reasoning.
Possible Solutions: If the tick is 10% greater than the tick before and after it, remove it as it is noise when deciding generalizing patterns.

(See extreme outliers)


<hr style="border: 2px solid grey;">

### Formatted Data:
This data was valid, but didn't have the right format to be valid for analysis, so it needed to be formatted correctly.

**Duplicate Timestamps:**

Under the assumption that multiple transactions can happen at the same timestamp,
I cleaned the data, then added to the dataset. The cleaning was necessary because during ohlcv generation, if the start/end time input is a timestamp that has a duplicate entry, there would be no nonbias way to pick and choose which duplicate to pick.
* I assumed that the approach of averaging the prices and combining the volume would suffice, and therefore only let the ohlcv interface pick one timestamp rather than pick from a plethora of.

```python
if row_timestamp in seen_keys:
    if input_str in data_dict.data_list.get(key).rows: #check for any duplicate entries
        print(f"duplicate entry found! {input_str}")
        continue
    # if row_timestamp not in duplicates:
    #     duplicates[row_timestamp] = [row_timestamp, float(input_str[1]), int(input_str[2]), 1]
    else:
        dupe_count = duplicates.get(row_timestamp)[3]
        curr_avg =duplicates.get(row_timestamp)[1]
        duplicates.get(row_timestamp)[1] = (price + curr_avg*dupe_count) / (dupe_count + 1) #calculate average of the duplicates to be used for data
        duplicates.get(row_timestamp)[2] += volume #calculate total volume to be used for data
        duplicates.get(row_timestamp)[3] += 1
        data_dict.data_list.get(key).ohlcv_bucket(row_timestamp, duplicates.get(row_timestamp)[1], volume, input_str) #handle duplicates in ohlcv calculation
    continue
```
<hr style="border: 2px solid grey;">

### Criteria that was Checked but had no anomalies:

**Timestamp Errors:**

In the first runthrough of my code, I detected zero timestamp formatting errors and thus had to do no discarding or cleaning based on a timestamp error.

```python
try:
    row_timestamp = datetime.strptime(input_str[0], "%Y-%m-%d %H:%M:%S.%f")
        #set the key for the dictionary entry
        key = row_timestamp.replace(microsecond=0)
    except ValueError:
            continue
        # skip data that has invalid timestamp
```

**Negative volume:**

I included methods to catch negative volume and discard it, however it was not present.

```python
if volume < volume_lower_bound:
    continue
```

**Zero volume:**

I included methods to catch volumes of zero and discard it, however it was not present.

```python
if volume == 0: #check for empty volumes
    continue
```

**Duplicate Data Points**

* I included methods to catch duplicate entries with exact time stamp, price, and volume, but couldn't find any. 
```python
if input_str in data_dict.data_list.get(key).rows: #check for any duplicate entries
    print(f"duplicate entry found! {input_str}")
    continue
```

<hr style="border: 2px solid grey;">

# Interface Preperation
As part of the cleaning process, I used a dictionary with each key being a second of time (e.g. 2024-09-16 12:20:25), 
and each key would map to a bucket that contains the raw data that happened within the second along with
the ohlcv values evaluated at the millisecond entries in the timestamp's second.
If the tick data is usable by passing all of the criteria below for subsequent analysis, I cleaned and prepared it for ohlcv generation by calculating the ohlcv values within the tick data's second.
* This step of data cleaning ensured that the data was ready to be used for ohlcv analysis.


1. After the tick is fully cleaned and confirmed valid, I first checked to see if a data bucket exists for the key that is the second the trade occurred.
```python
elif key not in data_dict.data_list.keys():
    data_dict.data_list[key] = DataBucket(key) #create DataBucket
```
2. Then, with the new or existing data bucket, I called a method I created within the data bucket to calculate the ohlcv values within the second the tick data occured.
```python
data_dict.data_list.get(key).ohlcv_bucket(row_timestamp, price, volume, input_str) #evaluate ohlcv for interval of the second
```
3. The tick data is then combined with other ticks that occurred within the same second. This method compares the time and price with the current ohlcv values and adds the volume to construct the new ohlcv values.

```python
def ohlcv_bucket(self, curr_time, price, volume, row):
    if curr_time <= self.open_time:
        self.open_time = curr_time #open_time to current time if current time is earlier than open_time
        self.open_price = price #set open_price to current price
    if curr_time >= self.close_time:
        self.close_time = curr_time #set close_time to current_time if current_time later than close_time
        self.close_price = price #set close_price to current price
    if self.high_price is None or price > self.high_price:
        self.high_price = price #price to the highest price if price more than high price
    if self.low_price is None or price < self.low_price:
        self.low_price = price #price to the lowest price if price less than high price
    self.volume += volume #add to total volume in the second
    self.rows.append(row) #add tick to raw data
```

4. When data processing is complete, the generation of ohlcv files in the interface phase will be much more efficient, since all the computations were pre-calculated.



