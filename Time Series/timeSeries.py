import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from statsmodels.tsa.arima_model import ARIMA
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 15, 6

path = 'D:/Application/eclipse/workspace/COMSE6998PROJECT/daodao_temp/'
fileName = 'cleanData_yellow_tripdata_2016-03.csv'

data = pd.read_csv(path + fileName)
del data['Unnamed: 0']

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

days = {}

df = pd.DataFrame(['hello', 'world'], columns=['words'])
for date in dates:
    for hour in hours:
        time = '2016-03-'+ date + ' ' + hour
        #count = data.tpep_pickup_datetime.str.contains(time).sum()
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
time_df.to_csv('out.csv')


dateparse = lambda dates: pd.datetime.strptime(dates, '%Y-%m-%d %H')
time_df = pd.read_csv('out.csv', parse_dates = ['time'], index_col = ['time'], date_parser = dateparse)
ts = time_df['num']
dailyts = ts['2016-03-03 00':'2016-03-05 00']
plt.plot(dailyts)
ts_log = np.log(ts)
ts_log_diff = ts_log - ts_log.shift()

model = ARIMA(ts_log, order=(2, 1, 2))  
results_ARIMA = model.fit(disp=-1)  
plt.plot(ts_log_diff)
plt.plot(results_ARIMA.fittedvalues, color='red')
plt.title('RSS: %.4f'% sum((results_ARIMA.fittedvalues-ts_log_diff)**2))

from statsmodels.tsa.stattools import adfuller
def test_stationarity(timeseries):
    
    #Determing rolling statistics
    rolmean = pd.rolling_mean(timeseries, window=12)
    rolstd = pd.rolling_std(timeseries, window=12)

    #Plot rolling statistics:
    orig = plt.plot(timeseries, color='blue',label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    
    #Perform Dickey-Fuller test:
    print 'Results of Dickey-Fuller Test:'
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print dfoutput
