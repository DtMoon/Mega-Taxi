# -*- coding:utf-8 -*-

import calendar
import copy
import csv
import random
import traceback

from lxml import etree
import requests

# 格式化时间，将所有输入进来的时间都变成xx:51的形式
def nearHour(hour):
    if hour[-2:] == 'am':
        if hour[:2] == '12':
            hour = '0' + hour[2:-3]
            # 处理12:05 am这种情况
            if int(hour[2:4]) <= 26: return '00'
        else:
            hour = hour[:-3]
    else:
        if hour[:2] == '12':
            hour = hour[:-3]
        else:
            hour = str(int(hour[:-6]) + 12) + hour[-6:-3]
    minute = int(hour[-2:])
    if minute > 26:
        return hour[:-2].zfill(3) + '51'
    else:
        return str(int(hour[:-3]) - 1).zfill(2) + ':51'
    
def preprocessing(year, month, day, csvWriter_original, csvWriter_processed):

    date = year + month + day
    
    url = 'https://www.timeanddate.com/weather/@8479493/historic?month=%s&year=%s' % (month, year)
    params = {'n':'@8479493',
          'mode':'historic',
          'hd':date,
          'month':month,
          'year':year,
          'json':'1'}
    
    html = requests.get(url, params=params)
    selector = etree.HTML(html.text)
    content = selector.xpath('//*[@id="wt-his"]/tbody/tr')
    
    try:
        count = 0
        lastHour = '00'
        lastData = []
        for each in content:
            data = [x.xpath('text()')[0].encode('utf-8') for i, x in enumerate(each) if i != 1 and i != 5]
            csvWriter_original.writerow(data)
#         #     data[1] = data[1].replace(u'\xa0', u' ')
            hour = nearHour(data[0])
            # 跳过重复时间的数据
            if hour == lastHour: continue
            data[0] = day + ' ' + hour
            data[1] = data[1][:-5] if data[1] != 'N/A' else 'N/A'
            data[2] = data[2].strip('.') if data[2] != 'N/A' else 'N/A'
            data[3] = data[3][:-4] if data[3] != 'No wind' and data[3] != 'N/A' else data[3]
            data[4] = data[4][:-1] if data[4] != 'N/A' else 'N/A'
            data[5] = data[5][:-4] if data[5] != 'N/A' else 'N/A'
            data[6] = data[6][:-4] if data[6] != 'N/A' else 'N/A'
            # 如果第一个时间点不是00:51的话，就用下一个时间点填充
            if count == 0 and hour != '00:51':
                num = int(hour[:2])
                for i in range(num):
                    newData = copy.copy(data)
                    newData[0] = day + ' ' + str(i).zfill(2) + ':51'
                    count += 1
                    csvWriter_processed.writerow(newData)
            # 如果中间有数据缺失，就用上一时刻和下一时刻填充缺失的数据
            elif int(hour[:2]) - int(lastHour[:2]) != 1:
                # 缺失了num条数据
                num = int(hour[:2]) - int(lastHour[:2]) - 1
                for i in range(num):
                    newData = [day + ' ' + str(int(lastHour[:2]) + i + 1).zfill(2) + ':51']
                    newData.append(str(int(int(lastData[1]) + (int(lastData[1]) - int(data[1])) * 1.0 / num * (i + 1))) if lastData[1] != 'N/A' and data[1] != 'N/A' else 'N/A')
                    newData.append(random.choice([lastData[2], data[2]]))
                    newData.append(str(int(int(lastData[3]) + (int(lastData[3]) - int(data[3])) * 1.0 / num * (i + 1))) if lastData[3] != 'N/A' and data[3] != 'N/A' and lastData[3] != 'No wind' and data[3] != 'No wind' else 'N/A')
                    newData.append(str(int(int(lastData[4]) + (int(lastData[4]) - int(data[4])) * 1.0 / num * (i + 1))) if lastData[4] != 'N/A' and data[4] != 'N/A' else 'N/A')
                    newData.append(str(float(lastData[5]) + (float(lastData[5]) - float(data[5])) * 1.0 / num * (i + 1)) if lastData[5] != 'N/A' and data[5] != 'N/A' else 'N/A')
                    newData.append(str(int(int(lastData[6]) + (int(lastData[6]) - int(data[6])) * 1.0 / num * (i + 1))) if lastData[6] != 'N/A' and data[6] != 'N/A' else 'N/A')
                    count += 1
                    csvWriter_processed.writerow(newData)
            lastHour = hour
            lastData = data
            count += 1
            csvWriter_processed.writerow(data)
        if count != 24:
            # 最后的比如23::51缺失的时候，就用上一时刻的填充
            for i in range(24 - count):
                newData = copy.copy(lastData)
                newData[0] = day + ' ' + str(count + i).zfill(2) + ':51'
                count += 1
                csvWriter_processed.writerow(newData)
            print date + ' ' + str(count)
    except Exception:
        traceback.print_exc()
    
def main():
    
    '''
    Weather date for 2016-11-29 and 2016-11-30 is not suitable for my code.
    So I have to revise these two csv files manually.
    '''
    for year in ['2015', '2016', '2017']:
        for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
            f = open(r'weather_original/weather_%s_%s.csv' % (year, month), "wb")
            csvWriter_original = csv.writer(f)
            g = open(r'weather_processed/weather_%s_%s.csv' % (year, month), "wb")
            csvWriter_processed = csv.writer(g)
            columns = ['Time', 'Temp', 'Weather', 'Wind', 'Humidity', 'Barometer', 'Visibility']
            csvWriter_original.writerow(columns)
            csvWriter_processed.writerow(columns)
            for day in range(1, calendar.monthrange(int(year), int(month))[1] + 1):
#             for day in range(12, 13):
                preprocessing(year, month, str(day).zfill(2), csvWriter_original, csvWriter_processed)
#                 break
            f.close()
            g.close()
#             break
#         break
        
if __name__ == '__main__':
    main()



