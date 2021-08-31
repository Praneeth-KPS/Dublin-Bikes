import requests
import json
import pymysql
import time
import traceback
import datetime

NAME="Dublin"
URL="https://api.jcdecaux.com/vls/v1/stations"
APIKEY="4ee14357926bd7f40f0598374fdf063fe64e402d"

conn = pymysql.connect(host='dublinbikes.caveezprtsl1.us-east-1.rds.amazonaws.com',user='michelle',password='booleRunnings',port=3306,database='dublinbikes')

def store(data):
    try:
        for i in range(len(data)):
            num = data[i]['number']
            name = data[i]['name']
            add = data[i]['address']
            lat = data[i]['position']['lat']
            lng = data[i]['position']['lng']
            bikeStands = data[i]['bike_stands']
            standsFree = data[i]['available_bike_stands']
            bikesFree = data[i]['available_bikes']
            status = data[i]['status']
            epoch = data[i]['last_update']
            if (epoch != None):
                update = datetime.datetime.fromtimestamp(epoch/1000).strftime("%Y-%m-%d %H:%M:%S")
                conn.cursor().execute('INSERT IGNORE INTO dublinbikes.dbikes (num,name,address,latitude,longitude,bike_stands,stands_free,bikes_free,status,last_update) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(num,name,add,lat,lng,bikeStands,standsFree,bikesFree,status,update))
                conn.commit() 
        
    except:
        print(traceback.format_exc())   
        
def main():
    while True:
        try:
            now = datetime.datetime.now()
            t = now.time()
            if not (t > datetime.time(0,30) and t < datetime.time(5,0)):
                r = requests.get(URL,params={"apiKey": APIKEY, "contract": NAME})
                data = json.loads(r.text)
                store(data)
                time.sleep(5*60)
        except:
            print(traceback.format_exc())     
    return

main()
