from crypt import methods
import os, requests
from flask import Flask, request

webport = os.getenv('AMT_API_PORT', default = 9393)
app = Flask(__name__)

amt_port = 9191

# Global vars:

bus_list = []
bus_added = set()
url_time = "http://127.0.0.1:9090/getime"
url_paline = "http://127.0.0.1:9090/paline"


  
# BUS FUNCTIONS:   

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
                    return b
                    

'''
    Route used to retrieve the information of a bus such as:
    - latitude, longitude and speed

    :param bus_id: Name of the bus to add in the net
'''
@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id,gps):
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
                speed = bus['speed']
                # speed = bus['speed']
                # speed *= 3.6
                return [str(lat),str(lon),speed]
    else:
        return "No bus founded with that ID"


'''
    Route used to clean the bus list after some specific
    action's flow. (see injection for more detail)

    :param bus_id: name of the bus
'''
@app.route("/busclean/<bus_id>", methods = ['POST'])
def cleanBus(bus_id):
    bus_id = request.form['bus']
    if(any(bus_id in x for x in bus_added)):
        bus_added.remove(bus_id)

# PALINE FUNCTIONS:

'''
    Route used to show all the upcoming
    busses in the chosen palina.
'''
@app.route("/palina/<palina_id>", methods = ['GET'])
def getPalina(palina_id):
    response = requests.get(url_paline)
    out = []
    if (response.status_code != 204 and response.status_code != 500 and
        response.headers["content-type"].strip().startswith("application/json")
        ):
        try:
            paline_list = response.json()
            for p in paline_list:
                if(palina_id in p):
                    s = "Bus " + p['bus'] + " arriving in " + p[palina_id]
                    out.append(s)
            return out
        except  ValueError:
            return "Error"
    else:
        return "Error"


'''
    Route used to retrieve the time of the 
    simulation (for the smart-display)
'''
@app.route("/getime", methods = ['GET'])
def getime():
    try:
        x = requests.get(url_time)
        if(x.status_code == 200): 
            return x.text
    except:
        print("error")

'''
    Main program
'''
if __name__ == '__main__':
    app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)