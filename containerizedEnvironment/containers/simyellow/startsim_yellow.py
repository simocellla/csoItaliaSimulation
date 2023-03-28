import os, requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
import prometheus_client
import json

webport = os.getenv('AMT_API_PORT', default = 9093)
app = Flask(__name__)

metrics = PrometheusMetrics(app)
time_metric = prometheus_client.Gauge('step', 'Step time')

# Global vars:

bus_list = []
bus_added = set()

#url_time = "http://127.0.0.1:9090/getime"
#url_paline = "http://127.0.0.1:9090/paline"

url_time = "http://10.254.254.100:9090/getime"
url_paline = "http://10.254.254.100:9090/paline"
 
 
# Implemented Routes:


'''
    Route implemented for update the information 
    about lat,lon and speed, for a chosen bus in the 
    scenario

    :param bus_id: (String) Name of the bus to update
'''
@app.route("/updatebus/<bus_id>", methods = ['POST'])
def update_bus(bus_id):
    global bus_list
    bus_added.add(bus_id)
    id = request.form['id']
    lat = request.form['lat']
    lon = request.form['lon']
    speed = request.form['speed']
    # print(str(lat),str(lon),str(speed))
    if not any(bus_['id'] == id  for bus_ in bus_list):
        bus = {}
        bus['id'] = bus_id
        bus['lat'] = lat
        bus['lon'] = lon
        bus['speed'] = speed
        # logica speed_list:
        bus['speed_list'] = []
        if(speed != None):
            bus['speed_list'].append(speed)
        bus_list.append(bus)
        return bus
    else:
        for b in bus_list:
            if(b['id'] == id):
                b['lat'] = lat
                b['lon'] = lon
                b['speed'] = speed
                if(speed != None):
                    b['speed_list'].append(speed)
                return b


'''
    Implemeted hello world for the Amt
    exposed API network
'''
@app.route("/")
def test():
    return "Amt exposed API --> Ok"


'''
    Route that shows the environment in use
'''
@app.route("/environment", methods = ['GET'])
def getEnvironment():
    return "Startsim_Yellow"


'''
    Route implemented in order to retrieve
    the name of all the bus in the running simulation
'''
@app.route("/busadded")
def hello():
    res = []
    if(len(bus_added) > 0):
        for bus in bus_list:
            name = bus['id']
            dict={'id':name}
            res.append(dict)
    return json.dumps(res)


'''
    Route implemented to retrieve the information of a bus such as:
    - latitude, longitude and speed

    :param <bus_id>: Name of the bus to add in the net
'''
@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id,gps):
    global bus_list
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
                speed = bus['speed']
                speed_list = bus['speed_list']
                # speed *= 3.6
                return [str(lat),str(lon),speed,speed_list]
    else:
        return "No bus founded with that ID"

'''
    Route implemented to retrieve in a JSON format
    the information of a bus such as:
    - latitude, longitude and speed

    :param <bus_id>: Name of the bus to add in the net
'''
@app.route("/buss/<bus_id>/<gps>", methods = ['GET'])
def get_gpss(bus_id,gps):
    global bus_list
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
                speed = bus['speed']
                speed_list = bus['speed_list']
                # speed *= 3.6
                out = {'lat':lat,'lon':lon,'speed':speed,'speed_list':speed_list}
                return json.dumps(out)
    else:
        return "No bus founded with that ID"


'''
    Route used to clean the bus list after some specific
    action's flow. (see injection.py for more detail)

    :param <bus_id>: (String) name of the chosen bus
'''
@app.route("/busclean/<bus_id>", methods = ['POST'])
def cleanBus(bus_id):   
    global bus_list
    bus_id = request.form['bus']
    if(any(bus_id in x for x in bus_added)):
        bus_added.remove(bus_id)
        for bus in bus_list:
            if(bus['id'] == bus_id):
                bus_list.remove(bus)
        return "Bus"+bus_id+"removed succesfully!"
    else:
        return "Problem in deleting bus"+bus_id


# PALINE FUNCTIONS:

'''
    Route used to show all the upcoming
    busses in the chosen smart display (palina).

    :param <palina_id>: (String) name of the chosen bus stop

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
                else:
                    return("No upcoming bus")
            return out
        except  ValueError:
            return "Error"
    else:
        return "No Upcoming Bus"


'''
    Route used to retrieve in a JSON format all the upcoming
    busses in the chosen smart display (palina).

    :param <palina_id>: (String) name of the chosen bus stop

'''
@app.route("/palinaa/<palina_id>", methods = ['GET'])
def getPalinaa(palina_id):
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
                    dict = {
                        'string':s
                    }
                    out.append(dict)
                else:
                    return("No upcoming bus")
            return json.dumps(out)
        except  ValueError:
            return "Error"
    else:
        return "No Upcoming Bus"


'''
    Route used to retrieve the current time 
    of the running simulation
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
    Route implemented for Prometheus
    in order to retrieve metrics of the running environment
'''
@app.route("/metrics")
def metrics():
    step = getime()
    time_metric.set(step)
    return prometheus_client.generate_latest()


'''
    Main program
'''
if __name__ == '__main__':
    app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)