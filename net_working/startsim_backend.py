from crypt import methods
import traci, os, threading, time, json, requests, math
from flask import Flask, request

simport = os.getenv('SIM_PORT', default = 8813)
simhost = os.getenv('SIM_HOST', default = 'localhost')
simlabel = os.getenv('SIM_LABEL', default = 'main')
webport = os.getenv('SIM_API_PORT', default = 9090)
delay = os.getenv('DELAY', default = 100)

traci.init(port=simport, host=simhost, label=simlabel)
conn = traci.getConnection(simlabel)

lock = threading.Lock()

app = Flask(__name__)


# Global Vars:

fermate_tot = []
bus_list = []
bus_added = set()
var_flow = 0
timetable =  []
bus_flow = set()
junctions = set()
junctions_list = []
step = 0
speed_list = []
index = []
time_analysis = 0
paline = []
fermate  = ["Marconi1-Fiera","Marconi2-Rimessa",
            "Italia1-PuntaVagno","Italia2-Piave","Italia3-Zara"]
total_distances = [206.34,
                    275.32,
                    348.89,
                    289.13,
                    301.13,
                    2457.82]


# LOCAL FUNCTION (updates...) :

''''
    Function called on each step of the simulation, 
    it will update a Dictionary that contains
    all the bus&information about them.
'''
def updateDict():
    for vehicleId in traci.vehicle.getIDList():
        if(traci.vehicle.getTypeID(vehicleId) == "DEFAULT_VEHTYPE"):
            speed = traci.vehicle.getSpeed(vehicleId)
            x, y = traci.vehicle.getPosition(vehicleId)
            lon, lat = traci.simulation.convertGeo(x, y)
            next_stops = traci.vehicle.getStops(vehicleId)
            stop_state = traci.vehicle.getStopState(vehicleId)
            people_in = traci.vehicle.getPersonNumber(vehicleId)
            bus_added.add(vehicleId)
            for bus in bus_added:
                if not any(bus_['id'] == vehicleId  for bus_ in bus_list):
                    # no exists
                    bus = {}
                    bus['id'] = vehicleId
                    bus['speed'] = speed
                    bus['lat'] = lat
                    bus['lon'] = lon
                    bus['stop_state'] = stop_state
                    bus['people_in'] = people_in
                    bus['speed_list'] = calculateAverageSpeedRunTime(vehicleID=vehicleId)
                    if(len(next_stops) > 0):
                        bus['bus_status'] = next_stops[0].stopFlags
                        bus['next_stop'] = next_stops[0].stoppingPlaceID
                    bus_list.append(bus)
                    print("Bus "+vehicleId+" added correctly")
                else:
                    for b in bus_list:
                        if(b['id'] == vehicleId):
                            b['speed'] = speed
                            b['lat'] = lat
                            b['lon'] = lon
                            b['stop_state'] = stop_state
                            b['people_in'] = people_in
                            b['speed_list'] = calculateAverageSpeedRunTime(vehicleID=vehicleId)
                            if(len(next_stops) > 0):
                                b['bus_status'] = next_stops[0].stopFlags
                                b['next_stop'] = next_stops[0].stoppingPlaceID
                                
        # if(len(bus_list) > 0 ): print(bus_list)


''''
    Function used to update all the paline informations
    about the desidered vehicleId

    :input vehicleId: bus on which we want to update the info
'''
def updatePaline(vehicleId):
    global paline
    fermate_remains = []
    if vehicleId in traci.vehicle.getIDList():
        for bus in bus_list:
            if(bus['id'] == vehicleId):
                if not any(paline_['bus'] == vehicleId for paline_ in paline): # Se non ci sono informazioni sul bus
                    next_stops = traci.vehicle.getStops(vehicleId)
                    if(not (len(next_stops) == 0)):
                        fermate_remains = getNextBusStops(vehicleId)
                        palina = {}
                        palina['bus'] = vehicleId
                        if(fermate_remains != None and len(fermate_remains) > 0):
                            for f in fermate_remains:
                                if f in fermate:
                                    palina[f] = showTimePalina(vehicleId,f)
                            paline.append(palina)
                else:
                    fermate_remains = getNextBusStops(vehicleId)
                    if(fermate_remains != None and len(fermate_remains) > 0):
                        for f in fermate:
                            if f in fermate_remains:
                                for pal in paline:
                                    if(pal['bus'] == vehicleId):
                                        pal[f] = showTimePalina(vehicleId,f)
                            else:
                                for pal in paline:
                                    if(pal['bus'] == vehicleId):
                                        if(f in pal):
                                            del pal[f]                    
        # if(len(paline) > 0): print(paline)

'''
    Function used to clean the remains
    paline in the paline list

    :input paline: list, all the paline in the simulation
'''
def cleanPaline(paline):
    if len(paline) > 0:
        for p in paline:
            for key, value in dict(p).items():
                if value == "Errore":
                    del p[key]       


'''
    Function used to retrieve the time to 
    get the desidered bus_stop with the vehicle

    :input vehicleId: str, bus name 
    :input palinaID: str, name of the bus stop to analyze
'''
def showTimePalina(vehicleId,palinaID):
    tot = 0
    global time_analysis, speed_list, paline, total_distances
    if(vehicleId in bus_flow and vehicleId in traci.vehicle.getIDList()):
        next_stops = traci.vehicle.getStops(vehicleId)
        if(len(next_stops) == 0):
            # Se finite fermate:
            for pal in paline:
                if(pal['bus'] == vehicleId):
                    paline.remove(pal)
            # return "Errore"
        else:
            next_stop = next_stops[0].stoppingPlaceID
            index.append(fermate.index(next_stop))
            if(palinaID in fermate and palinaID != next_stop):
                for i in range(fermate.index(next_stop),fermate.index(palinaID)+1):
                    tot += total_distances[i]
                dis = tot
            else:
                dis = total_distances[fermate.index(next_stop)]
            if(dis == 0):
                dis = total_distances[fermate.index(next_stop)] # TODO : solve the bug!
            if(len(index) >= 1):
                if(len(speed_list) > 0):
                    diff = step-time_analysis
                    average_ms = sum(speed_list)/len(speed_list)
                    if(diff > 0 and average_ms > 0):
                        space_did = diff*average_ms
                        dis_diff = dis-space_did
                        time_s = dis_diff/average_ms
                        if(time_s < 0):
                            time_s = 1
                        time_m = time_s/60
                        return str(math.ceil(time_m))
                    elif(diff == 0 and average_ms > 0):
                        time_s = (dis/average_ms)
                        if(time_s < 0):
                            time_s = 1
                        time_m = time_s/60
                        return str(math.ceil(time_m))
                    else:
                        return "Problem" # Se velocità = 0
        if(len(index) > 2):
            if(index[len(index)-1] != index[len(index)-2]):
                print("Cambio di time_analysis")
                time_analysis = step 


'''
    Function that allow to update the average speed of
    a desidere vehicleID
'''
def calculateAverageSpeedRunTime(vehicleID): 
    # TODO: change with dict
    global speed_list
    list_vehicle = traci.vehicle.getIDList() # already checked before calling this function
    if(vehicleID in bus_flow):
        if(vehicleID in list_vehicle):
            speed = traci.vehicle.getSpeed(vehicleID)
            #if(speed > 0.2): #maggiore di 5 km/h = 1.5 m/s
            speed_list.append(speed)
        else:
            speed_list = []
    else:
        speed_list = []
        #print("-speed list cleaned-")
    return speed_list


'''
    Function that update the list of upcoming 
    bus stops in the route of the chosen bus_id

    :input bus_id: String, name of the Bus
'''
def updateBusStop(bus_id):
    list_vehicle = traci.vehicle.getIDList()
    bus_stops = []
    if(any(bus_id in x for x in list_vehicle)):
        if(traci.vehicle.getTypeID(bus_id) == "DEFAULT_VEHTYPE"):
            next_stops = traci.vehicle.getStops(bus_id)
            for i in range(0,len(next_stops)):
                bus_stops.append(next_stops[i].stoppingPlaceID)
            if not any(bus_stop['bus'] == bus_id for bus_stop in timetable):
                _bus_stop = {}
                _bus_stop['bus'] = bus_id
                _bus_stop['time'] = bus_stops
                timetable.append(_bus_stop)
            else:
                for time in timetable:
                    if(time['bus'] == bus_id):
                        time['time'] = bus_stops
    #if(len(bus_stops) >0 ):return bus_stops
    

'''
    Function that updates the upcoming next busstops
    of the given bus

    :input vehicleId: str, name of the Bus
'''
def getNextBusStops(vehicleId):
    if(vehicleId in bus_added):
        for b in bus_list:
            if(b['id'] == vehicleId):
                next_stop = b['next_stop']
                if(next_stop in fermate):
                    index = fermate.index(next_stop)
                    fermate_remains = fermate[index:]
                    return fermate_remains


''''
    Function that clean all the speed_list of 
    the bus that are not in the net.

    :input list_vehicle: list, all the vehicle in the net
'''
def speed_list_cleaner(list_vehicle):
    for bus in bus_flow:
        if(bus not in list_vehicle):
            for b in bus_list:
                if(b['id'] == bus):
                    b['speed_list'] = []
                    print("Bus",bus," # speed list cleaned")

# Routes: 

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
    Route POST that aims to add a SINGLE new bus

    :param bus_id: Name of the bus to add in the net
    es: curl -X POST 127.0.0.1:9090/bus/J4/ --> will add a new bus J4
'''
@app.route("/bus/<bus_id>", methods = ['POST'])
def add_single_bus(bus_id):
    if bus_id != None:    
        traci.vehicle.add(bus_id, "busRoute", typeID="DEFAULT_VEHTYPE")
        #traci.vehicle.setBusStop(bus_id,"bs_0",duration=15)
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
    with lock:
        #global bus_id_flow
        list_vehicle = traci.vehicle.getIDList()
        if(not any(bus_id in x for x in list_vehicle)):
            var_flow = 1
            bus_flow.add(bus_id)
            traci.vehicle.add(bus_id, "busRoute", typeID="DEFAULT_VEHTYPE")   
            return "Added Bus flow "+bus_id+'\n'


'''
    GET route used to retrieve the information of a 
    desidered bus stop and bus_id

    :input palina_id: String, name of the chosen bus stop
    :input bus_id: String, name of the bus that we want to have info
    e.s : 127.0.0.1:9090/palina/bs_2/AA000AA
'''
@app.route("/palina/<palina_id>/<bus_id>", methods=['GET'])
def showPalina(palina_id,bus_id):
    time = 10 # TODO implement the correct value retrieval
    if (palina_id is not None and bus_id is not None):
        if(any(bus_id in x for x in bus_added)):
            if (len(timetable) > 0):
                for time in timetable:
                    if(time['bus'] == bus_id):
                        if(palina_id in time['time']):
                            time = (10*(time['time'].index(palina_id) +1))
                            out = "Bus "+bus_id+" is arriving in "+str(time)+" min at "+palina_id+" "
                            people = next(v['people_waiting'] for v in fermate_tot if v['id'] == palina_id)
                            return out+" ,"+str(people)+" people are waiting on it"
                        else: return "Error with input"
            else: return "Error with input"
        else: return "Error with input"
    else: return "Error with input"

        
'''
    Function that every step of the simulation update the waiting
    people at every stop of the bus

    :input fermate: all the possible bus stops in the net
'''
def updateWaitingPeople(fermate):
    for f in fermate:
        if not any(_f['id'] == f for _f in fermate_tot):
                fermata = {}
                fermata['id'] = f
                fermata['people_waiting'] =  traci.simulation.getBusStopWaiting(f)
                fermate_tot.append(fermata)
        else:
            for ferm in fermate_tot:
                if(ferm['id'] == f):
                    ferm['people_waiting'] = traci.simulation.getBusStopWaiting(f)
    #if(len(fermate_tot) != 0): print(fermate_tot)


'''
    Route GET that aims to see the Traffic Light information of a 
    specified Junction

    :param junction: Name of the junction in which want to see info
'''
@app.route("/gettrafficlight/<junction>/", methods=['GET'])
def showTrafficLight(junction):
    try:
        if(junction is not None):
            if junction in junctions:
                for jun in junctions_list:
                    if(jun['id'] == junction):
                        return ("Phase of "+junction+": "+str(jun['phase'])+" GreenYellowRed: "+str(jun['gyr']))
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
                

'''@app.route("/palinasmart/<vehicleId>/<palinaId>", methods = ['GET'])
def printPalina(vehicleId,palinaId):
    global paline
    for pal in paline:
        if(pal['bus'] == vehicleId):
            if(palinaId in pal):
                return str(pal[palinaId])
            else:
                return "Check palina input"
        else:
            return "Check bus input"'''


'''
    Route used to retrieve the time of the current 
    simulation
'''
@app.route("/getime", methods = ['GET'])
def getTime():
    global step
    return str(step)


'''
    Route used to get all the busstop situation in
    the net
'''
@app.route("/paline", methods = ['GET'])
def getPaline():
    global paline
    if(len(paline) > 0):
        return paline
    else:
        return "No paline avaiable"
    

'''
    Routes GET that aims to see Latitude and Longitude of 
    the specified Bus

    :param bus_id: Name of the bus to analyze
'''    
@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id,gps):
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
                speed = bus['speed_list']
                # speed = bus['speed']
                # speed *= 3.6
                return [str(lat),str(lon),speed]
    else:
        return "No bus founded with that ID"

'''
    Function used to update every step of simulation
    the information of alla the junctions in the net
'''
def updateJunction():
    if(len(junctions) > 0):
        for j in junctions:
            if not any(junction['id'] == j for junction in junctions_list):
                print("entrato")
                junction = {}
                junction['id'] = j
                junction['phase'] =  traci.trafficlight.getPhase(j)
                junction['gyr'] = traci.trafficlight.getRedYellowGreenState(j)
                junctions_list.append(junction)
            else:
                for jun in junctions_list:
                    if(jun['id'] == j):
                        jun['phase'] = traci.trafficlight.getPhase(j)
                        jun['gyr'] = traci.trafficlight.getRedYellowGreenState(j)
    #print(junctions_list)



'''
    Main program:
'''
def simulation():
    global var_flow
    global bus_id_flow
    global step
    print("Starting simulation...")
    step = 0
    sim = 1
    list_vehicle = traci.vehicle.getIDList()
    while sim > 0:
        with lock:
            updateDict()
            sim = traci.simulation.getMinExpectedNumber() > 0
            conn.simulationStep()
            step += 1  
        if(var_flow != 0): # Se è stato usata la funzione flow prima
            list_vehicle = traci.vehicle.getIDList()
            speed_list_cleaner(list_vehicle=list_vehicle)
            for bus in bus_flow:
                calculateAverageSpeedRunTime(vehicleID=bus)
                updatePaline(vehicleId=bus)
            for bus_id_flow in bus_flow:
                if(not bus_id_flow in list_vehicle):
                    add_flow(bus_id_flow)
                    updateBusStop(bus_id_flow)
        if (delay - 50) > 0:
            time.sleep((delay - 50)/1000)
        #time.sleep(0.1)
    conn.close()


if __name__ == '__main__':
    print("Setted delay: ",delay)
    t1 = threading.Thread(target=lambda: app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()