import pymysql
import traceback
import json

conn = pymysql.connect(host='dublinbikes.caveezprtsl1.us-east-1.rds.amazonaws.com',user='michelle',password='booleRunnings',port=3306,database='dublinbikes')
 
def store(data):
    try:
        for i in range(len(data)):
            num = data[i]['number']
            name = data[i]['name']
            add = data[i]['address']
            lat = data[i]['latitude']
            lng = data[i]['longitude']
             
            conn.cursor().execute('INSERT INTO dublinbikes.stations (num,name,address,latitude,longitude) VALUES (%s,%s,%s,%s,%s)',(num,name,add,lat,lng))
            conn.commit() 
         
    except:
        print(traceback.format_exc())   
        
def main():
    try:
        with open("dublin.json") as jsonfile:
            data = json.load(jsonfile)
            store(data)
    except:
        print(traceback.format_exc())     
    return

main()
