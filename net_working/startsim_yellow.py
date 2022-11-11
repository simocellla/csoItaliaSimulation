from crypt import methods
import os
from flask import Flask, request
import requests

webport = os.getenv('AMT_API_PORT', default = 9393)
app = Flask(__name__)

amt_port = 9191

global bus_list
global bus_added
bus_list = []
bus_added = set()

# Utile mettere <bus_id> come parameter? i don't think so ...
# 'POST' action of the bus:
@app.route("/updatebus/<bus_id>", methods = ['POST'])
def update_bus(bus_id):
    bus_added.add(bus_id)
    lat = request.form['lat']
    lon = request.form['lon']
    speed = request.form['speed']
    # print(str(lat),str(lon),str(speed))
    for bus in bus_added:
        if not any(bus_['id'] == bus_id  for bus_ in bus_list):
            bus = {}
            bus['id'] = bus_id
            bus['lat'] = lat
            bus['lon'] = lon
            bus['speed'] = speed
            bus_list.append(bus)
            return bus
        else:
            for b in bus_list:
                if(b['id'] == bus_id):
                    b['lat'] = lat
                    b['lon'] = lon
                    b['speed'] = speed
                    return "gia dentro\n"

# 'GET' information of the bus:
@app.route("/bus/<bus_id>", methods = ['GET'])
def get_gps(bus_id):
    for bus in bus_added:
        if any(bus_['id'] == bus_id  for bus_ in bus_list):
            for bus in bus_list:
                if(bus['id'] == bus_id):
                    lat = bus['lat']
                    lon = bus['lon']
                    speed = bus['speed']
                return ["Bus "+bus_id+":"+str(lat)+","+str(lon),"speed: "+str(speed)]
    else:
        print(bus_id,bus_list)
        return "No bus founded with that ID"


# 'GET' information of the Palina:
@app.route("/printpalina/<palina_id>", methods = ['GET'])
def printPalina(palina_id):
    url = "http://127.0.0.1:9090/timepalina/"+palina_id
    response = requests.get(url)
    if (response.status_code != 204 and response.status_code != 500 and
        response.headers["content-type"].strip().startswith("application/json")
        ):
        try:
            return response.json()
        except  ValueError:
            return 0
    else:
        return 0

if __name__ == '__main__':
    app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)