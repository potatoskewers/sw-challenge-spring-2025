# Cardinal Trading Group OHLCV File Interface
### Table of Contents:
1. [Description](#description)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Examples](#examples)
6. [Limitations](#limitations-to-the-interface)
7. [Assumptions Made](#assumptions-about-interface)

<hr style="border: 2px solid grey;">

## Description
This interface generates Cardinal Trading Group OHLCV (Open, High, Low, Close, Volume) tick data at each interval within a specified time range. The program is divided into three phases: 
* **Data Loading:** Loads the data into memory to prepare for cleaning
* **Data Cleaning:** Data is then cleaned by removing invalid and irrelevant data, and by fixing unusable datapoints
* **Data Interface:** Provides the user with a terminal-based interface to request OHLCV csv files

<hr style="border: 2px solid grey;">

## Features
The following are key features about the interface's design:
* **Multithreading** makes the data load more efficient by processing and cleaning multiple files at the same time.
* **Publish-subscribe pattern** is implemented by using queues to properly scale workloads for file loading and data cleaning workers, as well as to guarrent thread safety 
* **Abstracts** and pre-calculates OHLCV for each second to speed up the ohlcv file generation process.
* **Aggregates** duplicate timestamps so that ohlcv file generation doesn't have to pick and choose which timestamp to pick if the duplicate is a start or end interval.
* **Detects** and removes data errors found in datasets.
* **Noise** reduction by abstracting away irrelevant tick data.
* **Multiple** OHLCV files can be produced with the same data loaded into memory 

<hr style="border: 2px solid grey;">

## Installation
Step-by-step guide on how to set up and install dependencies.
1. Copy and paste the block below into your terminal

```bash
    git clone https://github.com/potatoskewers/sw-challenge-spring-2025.git 
```

<hr style="border: 2px solid grey;">

## Usage
1. First, navigate to the directory that the source code was installed to 
    * Example:
```bash
    cd ../Desktop/sw-challenge-spring-2025
```
2. Run the ```main.py``` program in your terminal:
* **NOTE:** you must have python installed on your computer to run this file. Follow instructions on 
how to do so here: https://www.python.org/downloads/

3. Wait for the data to finish loading indicated by the message "Data Cleaning Complete!" in terminal, and then in the terminal type in the interval, start time, end time
   * the interval is in the format of 'xs', 'xm', 'xh', 'xd', etc and can support combinations in the format of 'xs,xm,xh,xd' , 'xs,xs,xs' , 'xm'  where x is any positive integer and s, m, h, d represent units of time.
   * the start and end time must be in the format of 'Y-m-d H:M:S' where Y represents year, m represents month, d represents day, H represents hour, M represents minute, and S represents second.
4. The generated files will be at the directory specified. You may keep requesting ohlcv files after that
5. Afterwards, type "quit" to stop the program
## Examples:
Example usages in terminal:
![Screenshot 2025-02-09 at 6.49.24 PM.png](example-screenshots/Screenshot%202025-02-09%20at%206.49.24%E2%80%AFPM.png)
Example of common input errors :
![Screenshot 2025-02-09 at 6.49.40 PM.png](example-screenshots/Screenshot%202025-02-09%20at%206.49.40%E2%80%AFPM.png)
Example of quitting the interface:
![Screenshot 2025-02-09 at 6.50.27 PM.png](example-screenshots/Screenshot%202025-02-09%20at%206.50.27%E2%80%AFPM.png)
Example of an ohlcv file, produced in the first example.
![Screenshot 2025-02-09 at 6.51.08 PM.png](example-screenshots/Screenshot%202025-02-09%20at%206.51.08%E2%80%AFPM.png)

<hr style="border: 2px solid grey;">

## Limitations to the interface
The following are limitations to the interface's current release:
* Can only support English input and output
* Can be slower if machine has low memory capacity
* If an interval lacks a valid start or end timestamp data, both are shifted by a second until a match is found. With high-frequency data, intervals can be rarely contiguous, so the design ensures efficient handling of gaps.
* Can only check for outliers beyond 3 standard deviations
* Only supports intervals during market hours trading (09:30:00 AM - 04:30:00 EST)

<hr style="border: 2px solid grey;">

## Assumptions about interface
The following are assumptions in the Cardinal Trading Group tick data in accordance to creating the interface and cleaning the data
* All extreme outliers (<10%) are invalid data entries and thus need to be deleted from dataset
* Cardinal Trading Group Stock supports trading during after hour market hours
* After hour market hours do not hold enough liquidity to be considered significant
* Trades can occur simultaneously at the same timestamp, and duplicates must be aggregated by totaling all the duplicates volumes and averaging the prices of the duplicates 
* Small trades (<10) can be considered noise and thus negligible 