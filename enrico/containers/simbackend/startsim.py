import traci
import os 
import threading
import time 
import json 
import math
import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
import prometheus_client

simport = int(os.getenv('SIM_PORT', default=8813))
simhost = os.getenv('SIM_HOST', default='localhost')
simlabel = os.getenv('SIM_LABEL', default='main')
webport = int(os.getenv('SIM_API_PORT', default=9090))
delay = int(os.getenv('DELAY', default=100))

traci.init(port=int(simport), host=simhost, label=simlabel)
conn = traci.getConnection(simlabel)

lock = threading.Lock()

app = Flask(__name__)
metrics = PrometheusMetrics(app)
time_metric = prometheus_client.Gauge('step', 'Step time')


# Global Vars:

fermate_tot = []
bus_list = []
bus_added = set()
var_flow = 0
timetable = []
bus_flow = set()
junctions = set()
junctions_list = []
step = 0
speed_list = []
index = []
time_analysis = 0
paline = []
fermate = ["Marconi1-Fiera", "Marconi2-Rimessa", "Italia1-PuntaVagno", 
            "Italia2-Piave", "Italia3-Zara"]
total_distances = [206.34, 275.32, 348.89, 289.13, 301.13, 2457.82]
people_in = []
results = []
list_vehicle = []
people_bye = 0
people_byee = {} 
speed_lists = []
result = []


# LOCAL FUNCTION :


''''
    Function called on each step of the simulation, 
    it will update a Dictionary that contains
    all the bus&information about them.
'''
def updateDict(vehicleId):
    if(vehicleId in traci.vehicle.getIDList()):
        if(traci.vehicle.getTypeID(vehicleId) == "DEFAULT_VEHTYPE"):
            speed = traci.vehicle.getSpeed(vehicleId)
            x, y = traci.vehicle.getPosition(vehicleId)
            lon, lat = traci.simulation.convertGeo(x, y)
            next_stops = traci.vehicle.getStops(vehicleId)
            stop_state = traci.vehicle.getStopState(vehicleId)
            people_in = traci.vehicle.getPersonNumber(vehicleId)
            bus_added.add(vehicleId)
            #for bus in bus_added:
            if not any(bus_['id'] == vehicleId  for bus_ in bus_list):
                # no exists
                bus = {}
                bus['id'] = vehicleId
                bus['speed'] = speed
                bus['lat'] = lat
                bus['lon'] = lon
                bus['stop_state'] = stop_state
                bus['people_in'] = people_in
                # bus['speed_list'] = calculateAverageSpeedRunTimes(vehicleID=vehicleId)
                bus['speed_list'] = []
                bus['actual_speed'] = speed
                if len(results) > 0:
                    if any(vehicleId in dicts for dicts in results):
                        for p in results:
                            for key, value in dict(p).items():
                                if key == vehicleId:
                                    bus['score'] = value
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
                        b['actual_speed'] = speed
                        if(calculateAverage(vehicleId) != None):
                            b['speed_list'].append(calculateAverage(vehicleId))
                        else:
                            b['speed_list'] = retrievingSpeedList(vehicleId)
                        if len(results) > 0:
                            if any(vehicleId in dicts for dicts in results):
                                for p in results:
                                    for key, value in dict(p).items():
                                        if key == vehicleId:
                                            b['score'] = value
                        if(len(next_stops) > 0):
                            b['bus_status'] = next_stops[0].stopFlags
                            b['next_stop'] = next_stops[0].stoppingPlaceID


''''
    Function used to update all the paline informations
    about the desidered vehicleId

    :input vehicleId: bus on which we want to update the info
'''
def updatePaline(vehicleId):
    global paline
    global people_bye
    global people_byee
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
                                        if(pal[f] != None):
                                            if(f == "Marconi1-Fiera"): # TODO : retrieve the name by somewhere else!
                                                people_bye = 0
                                                if(int(pal[f]) > 50): # Se tempo > n le persone vanno via
                                                    # person = traci.busstop.getPersonIDs(f)
                                                    person = traci.person.getIDList()
                                                    if(len(person) > 0):
                                                        for p in person:
                                                            traci.person.remove(p)
                                                            people_bye += 1
                                                        print(people_bye,"person left simulation due to unexpected error")
                                                        if(people_bye > 0):
                                                            if not any('Marconi1-Fiera' in x for x in people_byee):
                                                                people_byee['Marconi1-Fiera'] = people_bye
                                                                people_bye = 0
                                                            else:
                                                                #if(people_byee['Marconi1-Fiera'] > 0):
                                                                people_byee['Marconi1-Fiera'] += people_bye
                                                                people_bye = 0
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

    :input vehicleId: String, name of the chosen vehicle
    :input palinaID: String, name of the chosen bus stop
'''
def showTimePalina(vehicleId,palinaID):
    tot = 0
    sum = 0
    global time_analysis, speed_list, paline, total_distances
    if(vehicleId in list_vehicle):
        for b in bus_list:
            if(b['id'] == vehicleId):
                speed_list = b['speed_list']
                next_stops = traci.vehicle.getStops(vehicleId)
                if(len(next_stops) == 0):
                    # Se finite fermate:
                    for pal in paline:
                        if(pal['bus'] == vehicleId):
                            paline.remove(pal)
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
                            for i in speed_list:
                                if i != None:
                                    sum+=float(i)
                            average_ms = sum/len(speed_list)
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
                            elif(average_ms < 0):
                                average_ms = 0.001
                                time_s = (dis/average_ms)
                                if(time_s < 0):
                                    time_s = 1
                                time_m = time_s/60
                                return str(math.ceil(time_m))
                            else:
                                if(diff > 0):
                                    if(average_ms > 0):
                                        space_did = diff*average_ms
                                        dis_diff = dis-space_did
                                        time_s = dis_diff/average_ms
                                        if(time_s < 0):
                                            time_s = 0
                                        time_m = 150
                                        return str(math.ceil(time_m))
                                else:
                                    if(average_ms > 0):
                                        time_s = (dis/average_ms)
                                        if(time_s < 0):
                                            time_s = 0
                                        time_m = 150
                                        return str(math.ceil(time_m))
                                # return "Problem" # Se velocità = 0
                    if(len(index) > 2):
                        if(index[len(index)-1] != index[len(index)-2]):
                            # print("Cambio di time_analysis")
                            time_analysis = step 


'''
    Function that aims, to retrieve the speed of 
    the chosen vehicleID.

    :input vehicleID: String, name of the chosen vehicle
'''                    
def calculateAverage(vehicleID):
    list_vehicle = traci.vehicle.getIDList() # already checked before calling this function
    if(vehicleID in list_vehicle):
        try:
            #response = requests.get("http://127.0.0.1:9393/bus/"+vehicleID+"/aa")
            response = requests.get("http://10.254.254.101:5000/bus/"+vehicleID+"/aa")
            if(response.status_code == 200):
                bus_info = response.json()
                #speed = bus_info[2]
                speed_list = bus_info[3]
                if(len(speed_list) > 0):
                    if speed_list[-1] != None:
                        return speed_list[-1]
                    else:
                        raise Exception
                else:
                        raise Exception
        except:
            speed = traci.vehicle.getSpeed(vehicleID)
            return speed


'''
    Function that at each step of the simulation 
    update the speed_list value for each bus in the scenario.

    :input vehicleId: String, name of the chosen vehicle
'''
def updateListSpeeds(vehicleId):
    global speed_list
    global speed_lists
    if(vehicleId in list_vehicle):
        speed = calculateAverage(vehicleId)
        if (len(speed_lists) > 0):
            if (any(vehicle_dict['id'] == vehicleId for vehicle_dict in speed_lists)): # Se c'è già
                for vehicle_dicts in speed_lists:
                    if vehicle_dicts['id'] == vehicleId:
                        if(speed != None):
                            vehicle_dicts['speed_list'].append(speed)
                            #print(vehicleId,"added speed",speed)
            else: # se non c'è ancora
                dictionary = {'id':vehicleId,'speed_list':[]}
                speed_lists.append(dictionary)
        else:
            dictionary = {'id':vehicleId,'speed_list':[]}
            speed_lists.append(dictionary)


'''
    Function that aims to retrieve, given the vehicleId,
    the speed_list list of the vehicle.

    :input vehicleID: String, name of the chosen vehicle
'''
def retrievingSpeedList(vehicleId):
    if(len(speed_lists)>0):
        for vehicle_dict in speed_lists:
            if vehicle_dict['id'] == vehicleId:
                return vehicle_dict['speed_list']

    
'''
    Function that update the list of the waiting people
    for each of the bus stops in the scenario.
'''
def updateWaitingPeopleS():
    global people_in
    for bus_stop in fermate:
        if not any(_f['id'] == bus_stop for _f in people_in):
            fermata = {}
            list_people = []
            fermata['id'] = bus_stop
            people_wait = traci.simulation.getBusStopWaiting(bus_stop) # TODO : to change
            if(people_wait > 0):
                if(people_bye > 0): people_wait -= people_bye
                list_people.append(people_wait)
                fermata['people_waiting'] =  list_people
            else:
                list_people = []
                fermata['people_waiting'] = list_people
            people_in.append(fermata)
        else:
            for ferm in people_in:
                if(ferm['id'] == bus_stop):
                    people_wait = traci.simulation.getBusStopWaiting(bus_stop)
                    if(people_bye > 0): people_wait -= people_bye
                    if(people_wait > 0):
                        ferm['people_waiting'].append(people_wait)
    if(len(people_in) > 0): 
        # print("People in",people_in)
        return people_in
    

'''
    Function used to retrieve the number of people
    that were waiting to pick the bus up.

    :input people_in: List, list of dictionaries in this form 
                            (key:name of the bus stop,
                            value: number of people waiting the bus) 
    :input busStopId: String, name of the chosen bus stop
'''
def getFermPeople(people_in, busStopId):
    people_left = 0
    busStopId = "Marconi1-Fiera"
    for ferm in people_in:
        if(ferm['id'] == busStopId):
            if(len(ferm['people_waiting']) > 2):
                for i in range(1,len(ferm['people_waiting'])):
                    if(len(ferm['people_waiting']) > 0):
                        if(ferm['people_waiting'][i] < ferm['people_waiting'][i-1]):
                            people_left = ferm['people_waiting'][i-1] # Salite sull'autobus
                            # res.append(people_left)
                            bus_stop = ferm['id']
                            ferm['people_waiting'] = []
                            if(len(people_byee) > 0):
                                if(people_byee[bus_stop] > 0): #and people_byee[bus_stop] < people_left):
                                    people_left -= people_byee[bus_stop]
                        '''else:                              
                            if(len(people_byee) > 0 and people_byee[busStopId] > 0):
                                people_left = people_byee[busStopId]'''
            bus_stop = busStopId
    if(people_left <= 0): people_left = 1
    return people_left,bus_stop


'''
    Function used to compute the score of the bus

    :input vehicleId: String, name of the bus
'''
def computeScoreBus(vehicleId):
    global results
    fermate_remain = set()
    if(vehicleId in list_vehicle):
        for item in traci.vehicle.getStops(vehicleId):
            fermate_remain.add(item.stoppingPlaceID)
        #for fer in fermate:
        fer = "Marconi1-Fiera"
        if(fer not in fermate_remain and len(fermate_remain) > 1):
        #if(fer == "Marconi1-Fiera"):
            result = getFermPeople(updateWaitingPeopleS(),fer)
            if(result is not None):
                people_left = result[0]
                bus_stop = result[1]     
                if any(bus_['id'] == vehicleId for bus_ in bus_list):                        
                    for b in bus_list:
                        if(b['id'] == vehicleId):
                            if(fer == bus_stop): 
                                score = (b['people_in']/(people_left)*100)
                                if score >= 100:
                                    score = 100
                                # se c'è già qualcosa dentro alla lista di dict:
                                if(len(results) > 0):
                                    #if any(vehicleId in dicts for dicts in results): no necessary
                                    if any(vehicleId in p for p in results): 
                                        for p in results:
                                            for key, value in dict(p).items():
                                                if key == vehicleId:
                                                    if value != score:
                                                        p[key] = score
                                    else:
                                        d = {vehicleId:score}
                                        results.append(d)
                                else:   
                                    if score <= 100:
                                        d = {vehicleId:score}
                                        results.append(d)
                                    else:
                                        score = 100
                                        d = {vehicleId:score}
                                        results.append(d)
    fermate_remain = ()
    '''if (len(results) > 0):
        print(results)'''


'''
    Function that will keep updated some 
    necessary vars.

'''
def updateVariable():
    global var_flow
    list_vehicle = traci.vehicle.getIDList()
    for veh in list_vehicle:
        if(traci.vehicle.getTypeID(veh) == "DEFAULT_VEHTYPE" and veh not in bus_flow):
            bus_flow.add(veh)
            print("bus",veh,"added to bus flow")
    if(len(bus_flow) > 0):
        for v in bus_flow.copy():
            if v not in list_vehicle:
                bus_flow.remove(v)
    '''if(len(bus_flow) > 0):
        var_flow = 1
    else:
        var_flow = 0'''


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
    global speed_lists
    for bus in bus_flow:
        if(bus not in list_vehicle):
            for b in bus_list:
                if(b['id'] == bus):
                    b['speed_list'] = []
                    print("Bus",bus,"# speed list cleaned")
                    if len(speed_lists) > 0:
                        for vehicle_dict in speed_lists:
                            if vehicle_dict['id'] == b['id']:
                                vehicle_dict['speed_list'] = []
                                print("       # Speed lists cleaned")
    # Cleaning the bus_list
    for bus in bus_list:
        if bus['id'] not in list_vehicle:
            bus_list.remove(bus)
            print(bus['id'],"     # Bus removed")

'''
    Function that aims to clean all the information 
    of the bus that are not longer in the simulation

    input: list_vehicle: List, list of all the vehicles in the scenario.
'''
def cleanResults(list_vehicle):
    if(len(results) > 0):
        for p in results:
            for key, value in dict(p).items():
                if key not in list_vehicle:
                    results.remove(p)
                    print("Results of the bus cleaned",p,"deleted")
    else:
        return "None"


# Flask's implemented routes:

'''
    Hello world from Backend
'''
@app.route("/environment", methods = ['GET'])
def getEnvironment():
    type = "Startsim_Backend"
    msg = {'type':type}
    return json.dumps(msg)

'''
    Route used to retrieve the time of the current 
    simulation
'''
@app.route("/getime", methods = ['GET'])
def getTime():
    global step
    return str(step)

'''
    Route used to retrieve the time of the current
    simulation in a JSON format
'''
@app.route("/getimeJSON")
def timeJson():
    global step
    d = {"time":step}
    return d


'''
    Route used by Prometheus to gain metrics
'''
@app.route("/metrics")
def metrics():
    global step
    steps = 110
    time_metric.set(steps)
    return prometheus_client.generate_latest()


'''
    Route that will give in a JSON format
    all the calculated scores of the buses in the scenario.
'''
@app.route("/scorebus", methods = ['GET'])
def getScore(): 
    res = []
    if(len(results) > 0):
        for vehicleId in list_vehicle:
            if any(vehicleId in dicts for dicts in results):
                for p in results:
                    for key, value in dict(p).items():
                        if key == vehicleId:
                            d = {'bus':vehicleId,'score':value}
                            #return json.dumps(d)
                            res.append(d)
        return json.dumps(res)


'''
    Route that will give in a JSON format:
    latitude, longitude and number of people that are waiting
    for the bus in the Marconi1-Fiera bus stop
    (useful for Grafana)
'''
@app.route("/getpeoplewaiting", methods = ['GET'])
def getInfo():
    people_left = 0
    lat,lon = '44.396019','8.944441'
    busStopId = "Marconi1-Fiera"
    for ferm in people_in:
        if(ferm['id'] == busStopId):
            if(len(ferm['people_waiting']) > 0):
                people_left = ferm['people_waiting'][-1]
                if(len(people_byee) > 0):
                    if(people_byee[busStopId] > 0):
                        people_left -= people_byee[busStopId]
    if(people_left <= 0): people_left = 1
    out = {
        'lat':lat,
        'lon':lon,
        'people':people_left
    }
    return json.dumps(out)


'''
    Primary route, this will get the name of all the 
    vehicles in the Simulation
'''
@app.route("/")
def test():
    list = []
    global list_vehicle
    # with lock:
    # l = conn.vehicle.getIDList()
    for i in list_vehicle:
        dict = {'name':i}
        list.append(dict)
    final = {"item":list}
    return json.dumps(final)


'''
    Route that will give the speed_list and 
    the coordinates (lat&lon) of the chosen bus

    :input bus_id: String, name of the chosen bus
    :input gps: String
'''
@app.route("/getspeed/<bus_id>/<gps>", methods=['GET'])
def getSpeedVehicle(bus_id,gps):
    #with lock:
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                speed = bus['actual_speed']
                return str(speed)


'''
    POST route that aims to add a SINGLE new bus

    :param bus_id: (String) Name of the bus to add in the net
    usage: 
        curl -X POST IP:PORT/bus/J4/  --> will add a new bus J4
'''
@app.route("/bus/<bus_id>", methods = ['POST'])
def add_single_bus(bus_id):
    if bus_id != None:  
        #with lock:  
        traci.vehicle.add(bus_id, "busRoute", typeID="DEFAULT_VEHTYPE")
        return json.dumps(request.form)
    else:
        return "Problem occured"


'''
    POST route that aims to add a FLOW of new bus

    :param bus_id: Name of the bus to add in the net
    usage: 
        curl -X POST IP:PORT/busflow/J4 --> will add a new bus J4 in a flow mode
'''
@app.route("/busflow/<bus_id>", methods = ['POST'])
def add_flow(bus_id):
    global var_flow
    global bus_flow
    with lock:
        #list_vehicle = traci.vehicle.getIDList()
        if(not any(bus_id in x for x in list_vehicle)):
            var_flow = 1
            bus_flow.add(bus_id)
            traci.vehicle.add(bus_id, "busRoute", typeID="DEFAULT_VEHTYPE")   
            return "Added Bus flow "+bus_id+'\n'


'''
    Route made for making injection to the desired bus
'''
@app.route("/executeinjection/<bus_id>", methods=['POST'])
def injection(bus_id):
    os.system('python3 injection_speed.py 31 -10')
    return "Attack Done!"


'''
    GET route used to retrieve the information of a 
    desidered bus stop and bus_id

    :input palina_id: String, name of the chosen bus stop
    :input bus_id: String, name of the bus that we want to have info
    usage:
        GET IP:PORT/palina/<palina_id>/<bus_id>
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

    :input fermate: List, all the bus stops in the net
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
    Route used to get all the busstop information in
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
    Route used to get all the busstop information in
    the net in a JSON format
'''
@app.route("/palinee", methods = ['GET'])
def getpaline():
    global paline
    if(len(paline) > 0): 
        #list = '\n'.join([str(d) for d in paline])
        return json.dumps(paline)
    else:
        return "No paline avaiable"


'''
    Routes GET that aims to see Latitude and Longitude of 
    the specified Bus

    :param bus_id: String, name of the bus to analyze
'''    
@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id,gps):
    #if(any(bus_id in x for x in bus_added)):
    if any(bus_['id'] == bus_id  for bus_ in bus_list):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
                speed = bus['speed_list']
                return [str(lat),str(lon),speed]
    else:
        return "No bus founded with that ID"


'''
    Route implemented to retrieve the lat&lon
    of a chosen <bus_id>

    :input <bus_id>: String, name of the chosen bus
'''
@app.route("/latlon/<bus_id>", methods = ['GET'])
def getLatLon(bus_id):
    if(any(bus_id in x for x in bus_added)):
        for bus in bus_list:
            if(bus['id'] == bus_id):
                lat = bus['lat']
                lon = bus['lon']
                dict = {'lat':lat,'lon':lon}
                return json.dumps(dict)


'''
    Route implemented to retrieve the lat&lon
    of all the buses in the scenario
'''
@app.route("/latlontotal", methods = ['GET'])
def getPositionTot():
    out = []
    for bus_id in list_vehicle:
        if(any(bus_id in x for x in bus_added)):
            for bus in bus_list:
                if(bus['id'] == bus_id):
                    id = bus['id']
                    lat = bus['lat']
                    lon = bus['lon']
                    dict = {'id':id, 'lat':lat, 'lon':lon}
                    out.append(dict)
    return json.dumps(out)





'''
    Main program:
'''
def simulation():
    global var_flow
    global bus_id_flow
    global step
    global list_vehicle
    print("Starting simulation...")
    step = 0
    sim = 1
    list_vehicle = traci.vehicle.getIDList()
    add_flow("A1")
    add_flow("A2")
    var_flow = 1
    while sim > 0:
        with lock:
            updateVariable()
            sim = traci.simulation.getMinExpectedNumber() > 0
            conn.simulationStep()
            step += 1
        if(var_flow != 0): # Se è stato usata la funzione flow prima
            list_vehicle = traci.vehicle.getIDList()
            updateWaitingPeopleS()
            speed_list_cleaner(list_vehicle=list_vehicle)
            cleanResults(list_vehicle)
            for bus in bus_flow:
                updateDict(bus)
                updateListSpeeds(bus)
                #calculateAverageSpeedRunTime(vehicleID=bus)
                updatePaline(vehicleId=bus)
                computeScoreBus(bus)
            for bus_id_flow in bus_flow:
                if(not bus_id_flow in list_vehicle):
                    add_flow(bus_id_flow)
        if (delay - 50) > 0:
            time.sleep((delay - 50)/1000)
    conn.close()


'''
    Main program
'''
if __name__ == '__main__':
    print("Setted delay: ",delay)
    t1 = threading.Thread(target=lambda: app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()