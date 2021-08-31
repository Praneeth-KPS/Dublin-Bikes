import pymysql
from sqlalchemy import create_engine
from jinja2 import Template
from flask import Flask, jsonify, render_template, request
import pandas as pd
from pandas import read_sql_query
import json
from functools import lru_cache
import requests
import pickle
import datetime

app = Flask(__name__)
    
@app.route("/")
def index():
    r = requests.get("http://api.weatherapi.com/v1/forecast.json?key=d0c63bd44623473da7394707212502&q=Dublin&days=1&aqi=no&alerts=no")
    data = json.loads(r.text)
    
    now = datetime.datetime.now()
    hour = int(now.strftime("%H"))
    
    weather = data['forecast']['forecastday'][0]['hour'][hour]

    hum = weather['humidity']
    cloud = weather['cloud']
    vis = weather['vis_km']
    uv = weather['uv']
    prec = weather['precip_mm']
    temp = weather['temp_c']
    ws = weather['wind_kph']
    gust = weather['gust_kph']
    feel = weather['feelslike_c']
    icon = weather['condition']['icon']

    return render_template("index.html", post=weather)

@app.route("/stations")
@lru_cache()
def stations():
    f = open('dynamickey.txt')
    line = f.readlines()
    converted_list = []

    for element in line:
        converted_list.append(element.strip())

    # initalising variables
    host = converted_list[0]
    db_name = converted_list[1]
    user_name = converted_list[2]
    password = converted_list[3]
    
    engine = create_engine(f'mysql+mysqlconnector://{user_name}:{password}@{host}:3306/{db_name}',echo=True)
    sql = "SELECT num,name,address,latitude,longitude FROM dublinbikes.stations;"
    df = pd.read_sql_query(sql, engine)
    return df.to_json(orient='records') 

@app.route("/dynamic")
def dynamic():
    f = open('dynamickey.txt')
    line = f.readlines()
    converted_list = []

    for element in line:
        converted_list.append(element.strip())

    # initalising variables
    host = converted_list[0]
    db_name = converted_list[1]
    user_name = converted_list[2]
    password = converted_list[3]
        
    db = pymysql.connect(host=host, user=user_name, passwd=password, db=db_name, port=3306)
    cursor = db.cursor()
    cursor.execute("SELECT name,num,bike_stands,stands_free,bikes_free, MAX(last_update) AS most_recent FROM dublinbikes.dbikes GROUP BY num;")
    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    # create an array to store the sql data
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    # convert the array to json format (default=str ensures dates are serializable) and return it
    return json.dumps(json_data,default=str)

@app.route("/occupancy/<int:station_id>")
def get_occupancy(station_id):
    db = pymysql.connect(host="dublinbikes.caveezprtsl1.us-east-1.rds.amazonaws.com", port=int(3306), user="michelle",
                         passwd="booleRunnings")
    cursor = db.cursor()
    sql = f"""select name, FLOOR(avg(bike_stands)) as Avg_bike_stands, FLOOR(avg(bikes_free)) as Avg_bikes_free, DAYNAME(last_update) as Week_Day_No from dublinbikes.dbikes 
        where num= {station_id} group by Week_Day_No order by Week_Day_No DESC;"""
    cursor.execute(sql)
    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()

    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))

    # convert the array to json format and return it
    return json.dumps(json_data)

@app.route("/hourly/<int:station_id>")
def get_Hourly(station_id):
    db = pymysql.connect(host="dublinbikes.caveezprtsl1.us-east-1.rds.amazonaws.com", port=int(3306), user="michelle",
                         passwd="booleRunnings")
    cursor = db.cursor()
    sql = f"""select name, count(num), FLOOR(avg(bike_stands)) as Avg_bike_stands, FLOOR(avg(bikes_free)) as Avg_bikes_free, EXTRACT(HOUR FROM last_update) as Hours from dublinbikes.dbikes 
    where num={station_id} group by Hours order by Hours asc;"""
    cursor.execute(sql)
    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()

    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))

    # convert the array to json format and return it
    return json.dumps(json_data)

@app.route("/predict/<int:station_id>/<int:hour>")
def predict(station_id,hour):
    
    r = requests.get("http://api.weatherapi.com/v1/forecast.json?key=d0c63bd44623473da7394707212502&q=Dublin&days=1&aqi=no&alerts=no")
    data = json.loads(r.text)
    
    weather = data['forecast']['forecastday'][0]['hour'][hour]

    hum = weather['humidity']
    cloud = weather['cloud']
    vis = weather['vis_km']
    uv = weather['uv']
    prec = weather['precip_mm']
    temp = weather['temp_c']
    ws = weather['wind_kph']
    gust = weather['gust_kph']
    feel = weather['feelslike_c']
    
    st = str(station_id)
    filename = 'station_' + st
    dbfile = open("models/" + filename, 'rb')     
    db = pickle.load(dbfile)
    dbfile.close()
    
    day = int(datetime.datetime.today().strftime('%w'))
    p = db.predict([[day,hour,hum,cloud,vis,uv,prec,temp,ws,gust,feel]]) # get a prediction
    freeBikes = str(p[0][0])
    
    json_data = []
    json_data.append([prec,temp,ws,gust,feel,freeBikes])
    data = json_data[0]
    return json.dumps(data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

if __name__ == "__main__":
    app.run(debug=True,port=8000)
