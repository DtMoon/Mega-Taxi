import os
import pandas as pd
import numpy as np

path = "./"
for readFileName in os.listdir(path + 'TaxiData/'):
    writeFileName = path + 'TaxiDataProcessed/cleanData_' + readFileName # TODO: change according to file name
    originalData = pd.read_csv(path + 'TaxiData/' + readFileName)
    
    data = originalData[originalData['RatecodeID'] == 1] # keep trips with standard rate
    del data['RatecodeID']
    del data['VendorID']
    del data['store_and_fwd_flag']
    del data['mta_tax']
    del data['improvement_surcharge']
    del data['extra']
    del data['tolls_amount']
    del data['passenger_count']
    
    data = data[data['payment_type'].isin([1, 2])] # only keep trips with payment type 1 or 2
    data = data[data['fare_amount'] > 0.0] # only keep trips with positive fare
    data = data[data['total_amount'] > 0.0] # only keep trips with positive fare
    
    # keep trips with appropriate longitudes and latitudes
    data = data[data['pickup_longitude'] != 0.0]
    data = data[data['pickup_latitude'] != 0.0]
    data = data[data['dropoff_longitude'] != 0.0]
    data = data[data['dropoff_latitude'] != 0.0]
    
    # only keep three digits after the decimal point for longitudes and latitudes
    data = data.round({'pickup_longitude': 3, 'pickup_latitude': 3})
    data = data.round({'dropoff_longitude': 3, 'dropoff_latitude': 3})
    
    # add a column "duration" to record the duration of each trip
    data['duration'] = pd.to_datetime(data['tpep_dropoff_datetime']) - pd.to_datetime(data['tpep_pickup_datetime'])
    
    # convert the timeDelta type to seconds
    data['duration'] = data['duration']/np.timedelta64(1, 's')
    data = data[data['duration'] > 0.0]
    del data['tpep_dropoff_datetime'] # delete the dropoff time column
    del data['payment_type']
    del data['fare_amount']
    del data['tip_amount']
    
    # keep coordinates in new york city
    data = data[data['pickup_longitude'] >= -74.043649]
    data = data[data['pickup_longitude'] <= -73.700512]
    data = data[data['pickup_latitude'] <= 40.916144]
    data = data[data['pickup_latitude'] >= 40.567813]
    
    data = data[data['dropoff_longitude'] >= -74.043649]
    data = data[data['dropoff_longitude'] <= -73.700512]
    data = data[data['dropoff_latitude'] <= 40.916144]
    data = data[data['dropoff_latitude'] >= 40.567813]
    
    data.to_csv(writeFileName, sep=',', index = False)