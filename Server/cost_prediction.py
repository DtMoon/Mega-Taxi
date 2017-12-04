
# coding: utf-8

# In[28]:


import socketserver
import json
from sklearn.externals import joblib
import simplejson
import urllib
import datetime
import numpy as np

vec = joblib.load('12_vec.pkl')
weekday_model = joblib.load('12_weekday_BestModel_RandomForestRegressor.pkl')
weekend_model = joblib.load('12_weekend_BestModel_RandomForestRegressor.pkl')

class MyServer(socketserver.BaseRequestHandler):

    def fetchTripInfo(self, origin, destination):
        url = "http://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=%s&destinations=%s&sensor=false&mode=driving"%(origin,destination)
        result= simplejson.load(urllib.urlopen(url))
        duration = result['rows'][0]['elements'][0]['duration']['value']
        trip_distance = result['rows'][0]['elements'][0]['distance']['text']
        return float(trip_distance[:-3]), float(duration)
    
    def predict_cost(self, client_data):
        origin = client_data.split('|')[0]
        destination = client_data.split('|')[1]
        data = self.fetchTripInfo(origin, destination)
        weather_forecast = json.load(open('weather_forecast.json'))
        hour = datetime.datetime.now().strftime('%H')
        weather = weather_forecast[hour][1:]
        data = data + (weather[0],weather[2],weather[3])
        dummyX = vec.transform([{'Weather':weather[1]}]).toarray()
        data = np.hstack([np.array(data),dummyX[0]])
        if datetime.datetime.now().weekday() <= 4:
            return weekday_model.predict(data)[0]
        else:
            return weekend_model.predict(data)[0]
    
    def handle(self):
        print ("服务端启动...")
        try:
            conn = self.request
            print (self.client_address)

            client_data = conn.recv(1024)
            print("client_data: "+client_data)

            cost = float("%.2f"%self.predict_cost(client_data))
            print cost

            conn.sendall(str(cost))
        except Exception as e:
            print(e)
        finally:
            print('connect close')
            conn.close()

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 38471), MyServer)
    print ('server starts')
    server.serve_forever()

