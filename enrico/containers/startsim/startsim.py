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

global var_flow
var_flow = 0
global bus_id_flow

'''
    Primary route, this will get the name of all the 
    vehicles in the Simulation
'''
@app.route("/")
def test():
    with lock:
        l = conn.vehicle.getIDList()
        return json.dumps(l)


'''
    Routes POST that aims to add a SINGLE new bus

    :param bus_id: Name of the bus to add in the net
    es: curl -X POST 127.0.0.1:9090/bus/J4/ --> will add a new bus J4
'''
@app.route("/bus/<bus_id>", methods = ['POST'])
def add_single_bus(bus_id):
    if bus_id != None:    
        traci.vehicle.add(bus_id, "line0", typeID="b_0")
        traci.vehicle.setBusStop(bus_id,"bs_0",duration=15)
        return json.dumps(request.form)
    else:
        return "Problem occured"


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

'''
    Routes POST that aims to see Latitude and Longitude of 
    the specified Bus

    :param bus_id: Name of the bus to analyze
    :param gps: # TODO???
'''       
@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id,gps):
    list_vehicle = traci.vehicle.getIDList()
    if(any(bus_id in x for x in list_vehicle)):
        if(traci.vehicle.getTypeID(bus_id) == "b_0"):
            x, y = traci.vehicle.getPosition(bus_id)
            lon, lat = traci.simulation.convertGeo(x, y)
            return [str(lon),str(lat)]
    else:
        return "No bus founded with that ID"


'''
    Routes that aims see the information of a smart display

    :param palina_id: Name of the busStop to analyze
    :param bus_id : Name of the Bus that we are waiting of
'''
@app.route("/palina/<palina_id>/<bus_id>", methods=['GET'])
def showPalina(palina_id,bus_id):
    time = 10 # TODO implement the correct value retrieval
    if (palina_id is not None and bus_id is not None):
        try:
            if(traci.vehicle.getTypeID(bus_id) == "b_0"):
                next_stops = traci.vehicle.getStops(bus_id)
                if(len(next_stops) > 0):
                    bus_status = next_stops[0].stopFlags   
                    bus_stop_id = next_stops[0].stoppingPlaceID
                    if(palina_id==bus_stop_id):
                        '''return("*******Palina ",bus_stop_id," ***********" + '\n' +
                        "Bus : ", bus_id, "is arriving in ",time, "min" + '\n' +
                                "*******************************************")'''
                        string = str(bus_id)+" is now arriving in "+str(time)+" min"
                        return(string)
        except traci.exceptions.TraCIException:
            return "Poblem with input"

'''
    Routes that aims to see the Traffic Light information of a 
    specified Junction

    :param junction: Name of the junction in which want to see info
'''
@app.route("/gettrafficlight/<junction>/", methods=['GET'])
def showTrafficLight(junction):
    #junction = "J4"
    try:
        if(junction is not None):
            phase = traci.trafficlight.getPhase(junction)
            gyr = traci.trafficlight.getRedYellowGreenState(junction)
            return ("Phase of "+junction+": "+str(phase)+" GreenYellowRed: "+str(gyr))

    except traci.exceptions.TraCIException:
        return "Problem with input"


'''
    Routes that aims to set the Traffic Light by specifing
    junction name and phase number

    :param junction: Name of the junction in which want to see info
    :param phase: Number of phase we want to set
'''
@app.route("/settrafficlight/<junction>/<phase>", methods=['POST'])
def setTrafficLight(junction,phase):
    #junction = "J4"
    try:
        if(junction is not None and phase is not None):
            traci.trafficlight.setPhase(junction,phase)
            return "Phase"+str(phase)+" setted on "+junction

    except traci.exceptions.TraCIException:
        return "Problem with input"


    
def simulation():
    global var_flow
    global bus_id_flow
    print("Starting simulation...")
    traci.route.add("line0", ["E0", "E18"]) # Definition of the line of the bus
    step = 0
    sim = 1
    while sim > 0:
        with lock:
            sim = traci.simulation.getMinExpectedNumber() > 0
            conn.simulationStep()
            step += 1
        if(var_flow != 0): # Se è stato usata la funzione flow prima
            add_flow(bus_id_flow)
        if (delay - 50) > 0:
            time.sleep((delay - 50)/1000)
        #time.sleep(0.1)
    conn.close()

if __name__ == '__main__':
    print("Setted delay: ",delay)
    t1 = threading.Thread(target=lambda: app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()