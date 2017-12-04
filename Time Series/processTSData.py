import os
import pandas as pd

dates = []
hours = []
for i in range(1, 32):
    if i < 10:
        dates.append('0' + str(i))
    else:
        dates.append(str(i))

for i in range(0, 24):
    if i < 10:
        hours.append('0' + str(i))
    else:
        hours.append(str(i))

path = '/Users/daodao/Documents/Columbia/COMSE6998/Final Project/PreProcessTaxiData/TaxiDataProcessed/'
for readFileName in os.listdir(path):
    month = readFileName.split('_')[-1].split('.')[0]
    data = pd.read_csv(path + readFileName)
    
    days = {}
    for date in dates:
        for hour in hours:
            time = month + '-' + date + ' ' + hour
            days[time] = 0
    
    for time in data['tpep_pickup_datetime']:
        days[time[:13]] += 1
    
    list_time = days.keys()
    list_time.sort()
    list_num = []
    for key in list_time:
        list_num.append(days[key])
    time_df = pd.DataFrame({'time': list_time, 'num': list_num})
    time_df.set_index('time', inplace = True)
    time_df.to_csv('/Users/daodao/Documents/Columbia/COMSE6998/Final Project/TimeSeries/Data/ts_' + month + '.csv')
