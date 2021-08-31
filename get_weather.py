import requests
import json
import pymysql
import time
import traceback
import datetime

conn = pymysql.connect(host='dublinbikes.caveezprtsl1.us-east-1.rds.amazonaws.com',user='michelle',password='booleRunnings',port=3306,database='dublinbikes')

def store(data):
    try:
        loc = data['location']['name']
        epoch = data['current']['last_updated_epoch']
        update = datetime.datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")
        temp = data['current']['temp_c']
        text = data['current']['condition']['text']
        ws = data['current']['wind_kph']
        wd = data['current']['wind_dir']
        prec = data['current']['precip_mm']
        hum = data['current']['humidity']
        cloud = data['current']['cloud']
        feel = data['current']['feelslike_c']
        vis = data['current']['vis_km']
        uv = data['current']['uv']
        gust = data['current']['gust_kph']
      
        conn.cursor().execute('INSERT INTO dublinbikes.weather (location,last_update,temp,text,wind_speed,wind_dir,prec,humidity,cloud,feel,vis,uv,gust) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(loc,update,temp,text,ws,wd,prec,hum,cloud,feel,vis,uv,gust))
        conn.commit()  

    except:
        print(traceback.format_exc())   
        
def main():
    while True:
        try:
            r = requests.get("http://api.weatherapi.com/v1/current.json?key=d0c63bd44623473da7394707212502&q=Dublin&aqi=no")
            data = json.loads(r.text)
            store(data)
            time.sleep(60*60)
        except:
            print(traceback.format_exc())     
    return

main()
