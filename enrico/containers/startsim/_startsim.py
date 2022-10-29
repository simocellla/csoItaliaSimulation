from crypt import methods
import traci
import os
import threading
import time
import json
from flask import Flask, request

simport = os.getenv('SIM_PORT', default = 8813)
simhost = os.getenv('SIM_HOST', default = 'localhost')
simlabel = os.getenv('SIM_LABEL', default = 'main')
webport = os.getenv('SIM_API_PORT', default = 9090)
delay = os.getenv('DELAY', default = 200)

traci.init(port=simport, host=simhost, label=simlabel)
conn = traci.getConnection(simlabel)

lock = threading.Lock()

app = Flask(__name__)

global bus_list 
bus_list = []
global bus_added
bus_added = set()
global var_flow
var_flow = 0

def updateDict():
    for vehicleId in traci.vehicle.getIDList():
        if(traci.vehicle.getTypeID(vehicleId) == "b_0"):
            speed = traci.vehicle.getSpeed(vehicleId)
            x, y = traci.vehicle.getPosition(vehicleId)
            lon, lat = traci.simulation.convertGeo(x, y)
            bus_added.add(vehicleId)
            for bus in bus_added:
                if not any(bus_['id'] == vehicleId  for bus_ in bus_list):
                    # no exists
                    bus = {}
                    bus['id'] = vehicleId
                    bus['speed'] = speed
                    bus['lat'] = lat
                    bus['lon'] = lon
                    bus_list.append(bus)
                else:
                    for b in bus_list:
                        if(b["id"] == vehicleId):
                            b["speed"] = speed
                            b['lat'] = lat
                            b['lon'] = lon
            
        if(len(bus_list) > 0 ): print(bus_list)

@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id,gps):
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
            return [str(lon),str(lat)]
    else:
        return "No bus founded with that ID"

'''
    Routes POST that aims to add a FLOW of new bus

    :param bus_id: Name of the bus to add in the net
    es: curl -X POST 127.0.0.1:9090/busflow/J4/ --> will add a new bus J4
'''
@app.route("/busflow/<bus_id>", methods = ['POST'])
def add_flow(bus_id):
    global var_flow
    global bus_id_flow
    with lock:
        list_vehicle = traci.vehicle.getIDList()
        if(not any(bus_id in x for x in list_vehicle)):
            var_flow = 1
            bus_id_flow = bus_id
            traci.vehicle.add(bus_id, "line0", typeID="b_0")        
            traci.vehicle.setBusStop(bus_id,"bs_0",duration=15)
            return "Added Bus flow "+bus_id+'\n'


def simulation():
    global var_flow
    global bus_id_flow
    print("Starting simulation...")
    traci.route.add("line0", ["E0", "E18"]) # Definition of the line of the bus
    step = 0
    sim = 1
    list_vehicle = traci.vehicle.getIDList()
    while sim > 0:
        updateDict()
        sim = traci.simulation.getMinExpectedNumber() > 0
        conn.simulationStep()
        step += 1       
        if(var_flow != 0): # Se è stato usata la funzione flow prima
            if(not any(bus_id_flow in x for x in list_vehicle)):
                add_flow(bus_id_flow)
        if (delay - 50) > 0:
            time.sleep((delay - 50)/1000)
        #time.sleep(0.1)
    conn.close()



if __name__ == '__main__':
    print("Setted delay: ",delay)
    t1 = threading.Thread(target=lambda: app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()