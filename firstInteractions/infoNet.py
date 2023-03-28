import sys, time
import traci
from sumolib import checkBinary
import traci.constants as tc

'''
    Simple program to retrieve in the Network:
            - Number of vehicles 
            - Vehicle infos (speed...)
            - People information
'''


def __init__():
    sumoBinary = checkBinary('sumo') # sumo or sumo-gui with visual view
    sumoConfig = "oldNetwork/002_new.sumocfg"
    sumoCmd = [sumoBinary, "-c", sumoConfig]
    traci.start(sumoCmd)
    print("--> Start Simulation")

vehiclesIDs=[]


def showVehicles():
    '''
    For every vehicles in the net this function prints:
        - Speed, Edge, Distance, GPS coordinates
    '''
    vehicles = traci.vehicle.getIDList()
    for v in vehicles:
        print("*",v, " infos:")
        print("Speed ", v, ":",traci.vehicle.getSpeed(v)*3.6, " km/h")
        print("EdgeID of veh ", v, ": ",traci.vehicle.getRoadID(v))
        print('Distance ', v, ": ",traci.vehicle.getDistance(v), " m")
        x, y = traci.vehicle.getPosition(v)
        lon, lat = traci.simulation.convertGeo(x, y)
        print("Coordinates of "+v+" ",lon,lat)
        print(" ")

def showPeople():
    '''
    For every person in the network this function shows:
        - Total people in the net
        - Waiting time of the person, vehicle which is riding on
    '''
    people = traci.person.getIDList()
    print("Total People: ",traci.person.getIDCount())
    for p in people:
        print("*",p,"infos:")
        # print("Speed: ", traci.person.getSpeed(p))
        print("Waiting time: ", traci.person.getWaitingTime(p))
        print("Vehicle: ",traci.person.getVehicle(p)),len(traci.person.getVehicle(p))

def isOnBus():
    '''
    Function that shows information about the bus in the net such as:
        - Road in which its riding, number of people inside the Bus
    '''
    people = traci.person.getIDList()
    bus = None
    road = None
    people_on = None
    for p in people:
        if(len(traci.person.getVehicle(p)) > 0):
            bus = traci.person.getVehicle(p)
            road = traci.vehicle.getRoadID(traci.person.getVehicle(p))
            people_on = traci.vehicle.getPersonIDList(traci.person.getVehicle(p))

    if(bus is not None):
        print("Bus: ",bus, " is now riding")
        print("on the: ", road, " road")
        print(len(people_on), "people are on the BUS")


def infoBusNet():
    '''
    Using subscriptions for retrieving Bus's information
    '''
    if(len(traci.simulation.getLoadedIDList())) > 0:
        #print("Vehicle in the net: ",traci.simulation.getLoadedIDList())
        for vehID in traci.simulation.getLoadedIDList():
            if(traci.vehicle.getTypeID(vehID) == "b_0"):
                vehiclesIDs.append(vehID)
                traci.vehicle.subscribe(vehID, (tc.VAR_PERSON_CAPACITY,tc.VAR_PERSON_NUMBER))
                print("Initial subscription for: ",vehID,": ",traci.vehicle.getSubscriptionResults(vehID))
                #if(len(traci.vehicle.getPersonIDList(vehID)) > 0): 
                '''print("---Found a BUS stopped:",vehID," ---")
                    print("CAPACITY ", traci.vehicle.getPersonCapacity(vehID))
                    print(traci.vehicle.getNextStops(vehID))
                    people_on = traci.vehicle.getPersonIDList(vehID)
                    print("PERSON IN ", len(people_on))'''

def printGPS(vehicleId = None):
    '''
    Function that aims to print the Longitude and Latitude of 
    a vehicle in the net

    :input vehicleId: String ID of the vehicle
    '''
    if vehicleId is not None:
        speed = traci.vehicle.getSpeed(vehicleId)
        x, y = traci.vehicle.getPosition(vehicleId)
        lon, lat = traci.simulation.convertGeo(x, y)
        print("Position of"+vehicleId+" ",lon,lat)
        print("Speed : ",speed)



if __name__ == "__main__":
    __init__()
    i = 0
    while(i < 3600):
        time.sleep(0.1)# Speed of simulation
        traci.simulationStep()
        if(i%10)==0:#Print only every 10sec
            showVehicles()
        i += 1
    if(i == 3600):
        traci.close()
        sys.exit("---> Finish Simulation")