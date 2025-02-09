# Description
This interface generates Cardinal Trading Group OHLCV (Open, High, Low, Close, Volume) tick data at each interval within a specified time range. The program is divided into three phases: 
* **Data Loading:** Loads the data into memory to prepare for cleaning
* **Data Cleaning:** Data is then cleaned by removing invalid and irrelevant data, and by fixing unusable datapoints
* **Data Interface:** Provides the user with a terminal-based interface to request OHLCV csv files

## Features
The following are key features about the interface's design:
* **Multithreading** makes the data load more efficient by processing multiple files at the same time
* **Abstracts** and pre-calculates OHLCV for each second to speed up the ohlcv file generation process.
* **Aggregates** duplicate timestamps so that ohlcv file generation doesn't have to pick and choose which timestamp to pick if the duplicate is a start or end interval.
* **Detects** and removes data errors found in datasets such as missing prices, missing volumes, negative prices, and extreme outliers
* **Noise** reduction by abstracting away irrelevant tick data

## Installation
Step-by-step guide on how to set up and install dependencies.
1. Copy and paste the block below into your terminal

```bash
    git clone https://github.com/potatoskewers/sw-challenge-spring-2025.git 
```

## Usage
1. First, navigate to the directory that the source code was installed to 
    * Example:
```bash
    cd ../Desktop/sw-challenge-spring-2025
```
2. Run the main program by executing the following in terminal:

```bash
    python main.py
```
3. Wait for the data to finish loading indicated by the message "Data Cleaning Complete!" in terminal, and then in the terminal type in the interval, start time, end time
   * the interval is in the format of 'xs', 'xm', 'xh', 'xd', etc and can support combinations in the format of 'xs,xm,xh,xd' , 'xs,xs,xs' , 'xm'  where x is any positive integer and s, m, h, d represent units of time.
   * the start and end time must be in the format of 'Y-m-d H:M:S' where Y represents year, m represents month, d represents day, H represents hour, M represents minute, and S represents second.
4. The generated files will be at the directory specified. You may keep requesting ohlcv files after that
5. Afterwards, type "quit" to stop the program
## Examples:

## Limitations to the interface
The following are limitations to the interface's current release:
* Can only support English input and output
* Can be slower if machine has low memory capacity

## Assumptions about interface
The following are assumptions in the Cardinal Trading Group tick data in accordance to creating the interface and cleaning the data
* All extreme outliers (<10%) are invalid data entries and thus need to be deleted from dataset
* Cardinal Trading Group Stock supports trading during after hour market hours
* After hour market hours do not hold enough liquidity to be considered significant
* Trades can occur simultaneously at the same timestamp, and duplicates must be aggregated by totaling all the duplicates volumes and averaging the prices of the duplicates 
* Small trades (<10) can be considered noise and thus negligible 