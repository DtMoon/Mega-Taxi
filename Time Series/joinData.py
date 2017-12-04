import os
import pandas as pd

data = []
fileNames = []
path = '/Users/daodao/Documents/Columbia/COMSE6998/Final Project/TimeSeries/Data/'
for fileName in os.listdir(path):
    fileNames.append(fileName)

fileNames.sort()
fileNames.pop(0)
for fileName in fileNames:
    data.append(pd.read_csv(path + fileName))
    
result = pd.concat(data, ignore_index = True)
result.to_csv('/Users/daodao/Documents/Columbia/COMSE6998/Final Project/TimeSeries/ts_data.csv', index = False)