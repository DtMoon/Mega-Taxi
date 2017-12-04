
# coding: utf-8

# In[13]:


import requests
from lxml import etree
import json

url = 'https://www.timeanddate.com/weather/@8479493//hourly'
html = requests.get(url)
selector = etree.HTML(html.text)
content = selector.xpath('//*[@id="wt-hbh"]/tbody/tr')

def processTime(t):
    if t[-2:] == 'am':
        if t[:2] == '12':
            return '00'
        return t.split(':')[0].zfill(2)
    else:
        if t[:2] == '12':
            return t.split(':')[0]
        return str(int(t.split(':')[0]) + 12)

def transferWeatherTypeToStandard(weatherType):
    weatherType = weatherType.split('.')[0].lower()
    for key in standardWeatherType:
        if weatherType in standardWeatherType[key]: return key
    return 'clear'

result = {}
standardWeatherType = json.load(open('WeahterTypes.json'))
for each in content:
    data = [x.xpath('text()')[0].encode('utf-8') for i, x in enumerate(each) if i in [0,2,3,5]]
    data[0] = int(processTime(data[0]))
    data[1] = float(data[1][:-5])
    data[2] = transferWeatherTypeToStandard(data[2])
    data[3] = float(data[3][:-4])
    data.append(0) # no visibility in the website
    result[data[0]] = data

