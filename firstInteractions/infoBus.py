import time
from requests import options
import traci
from sumolib import checkBinary
import sys

'''
    Simple program that aims to show the infos of the net
        - BUS : bus id, GPS coordinates, capacity, number of people in 
        - bus_stop : people that left the bus_stop after something...
'''

def __init__():
    sumoBinary = checkBinary('sumo-gui') # sumo or sumo-gui with visual view
    sumoConfig = "oldNetwork/002_new.sumocfg"
    sumoCmd = [sumoBinary, "-c", sumoConfig]
    traci.start(sumoCmd)
    print("--> Start Simulation")

def showBusBasicInfo():
    """
    Function that shows only information about the bus:
    type of vehicle, speed, coordinates, n people riding the bus
    """
    for vehicleId in traci.vehicle.getIDList():
        if(traci.vehicle.getTypeID(vehicleId) == "b_0"):
            speed = traci.vehicle.getSpeed(vehicleId)
            x, y = traci.vehicle.getPosition(vehicleId)
            lon, lat = traci.simulation.convertGeo(x, y)
            print("Type: ",traci.vehicle.getTypeID(vehicleId))
            print("Position of "+vehicleId+" ",lat,lon)
            print("Speed : ",speed*3.6, " km/h")
            #next_stops = traci.vehicle.getNextStops(vehicleId)
            next_stops = traci.vehicle.getStops(vehicleId)
            if(len(next_stops) > 0):
                bus_status = next_stops[0].stopFlags   
                bus_stop_id = next_stops[0].stoppingPlaceID         
                '''if len(next_stops) > 0:
                    if(next_stops[0][3] == 16 & traci.simulation.getBusStopWaiting(next_stops[0][2]) > 0): # if bus stopped and there are people waiting
                        print("Bus is taking passengers at bus stop: ",next_stops[0][2])
                        print("People on Bus Stop: ",traci.simulation.getBusStopWaiting(next_stops[0][2]))
                    else:
                        print("Next stop: ",next_stops[0][2])'''
                if(len(next_stops) > 0):
                    if(bus_status == 8 & traci.simulation.getBusStopWaiting(bus_stop_id) > 0): # if bus stopped and there are people waiting
                        print("Bus is taking passengers at bus stop: ",bus_stop_id)
                        print("People on Bus Stop: ",traci.simulation.getBusStopWaiting(bus_stop_id))
                    else:
                        print("Next stop: ",next_stops[0].stoppingPlaceID)
                people_in = traci.vehicle.getPersonNumber(vehicleId)
                if(people_in > 0):
                    print(people_in," person are now riding the bus")
                    print("***********************************************************")
            

def showBusInfoWhenStopped():
    '''
    Show basic information about the bus stop bs_0 (for now)
    [just to check if everything is consistent]
    '''
    for vehicleId in traci.vehicle.getIDList():
        if(traci.vehicle.getTypeID(vehicleId) == "b_0"):
            speed = traci.vehicle.getSpeed(vehicleId)
            bus_status = traci.vehicle.getStops(vehicleId)
            if(len(bus_status) > 0):
                print(bus_status)
                #bus_stop_id = traci.vehicle.getStops(vehicleId)[0].stoppingPlaceID
                #bus_status = traci.vehicle.getStops(vehicleId)[0].stopFlags
                bus_stop_id = bus_status[0].stoppingPlaceID
                bus_status = bus_status[0].stopFlags
                if(bus_status == 8): # waiting for pick/left passengers
                    people_waiting = traci.simulation.getBusStopWaiting("bs_0")
                    if(people_waiting > 0):
                        print(people_waiting, "people are waiting to be picked up at ",bus_stop_id)

def peopleWaitingAtBusStop(busStop=None):
    """
    Function that print the number of people that are 
    waiting to the busStop ID

    :input busStop: String, the ID of the bus stop
    """
    if busStop == None:
        bus_stop_ids = ["bs_0"] # Only the first one
        for bus_stop in bus_stop_ids:
            people_waiting = traci.simulation.getBusStopWaiting(bus_stop)
            if people_waiting > 0:
                print(people_waiting," people are waiting in ",bus_stop)
        people_waiting = 0

def peopleInOut(busStop= None, listPeople=None):
    # TODO : need to take as input the line, if not there will be some problem
    '''
    Function that aims to print the number of people that left the bus_stop

    :input bus_stop: String id of the bus_stop
    :input listPeople: list that will contains the number of people that are waiting
    :return: number of people that left the bus stop
    '''
    gold = 0
    if busStop == None:
        bus_stop_ids = ["bs_0"] # Only the first one, bs_3 is for the 2nd bus line
        for bus_stop in bus_stop_ids:
            people_waiting = traci.simulation.getBusStopWaiting(bus_stop)
            if people_waiting > 0:
                listPeople.append(int(people_waiting))
                #listPeople = list(set(listPeople))
            if len(listPeople) > 2:
                if(listPeople[len(listPeople) - 1] < listPeople[len(listPeople) - 2]):
                    gold = listPeople[len(listPeople)-2] + listPeople[len(listPeople) - 1]
                    print(gold, " have left the bus stop ",bus_stop)
                    last = listPeople[len(listPeople) - 1]
                    del listPeople[:]
                    listPeople = []
                    #listPeople.append(last)
        if gold != 0:
            return gold

def computeScore(n_people_waiting=None):
    '''
    Function that computes how many people in the bus_stop were
    able to take the bus (in %)
    '''
    #poeple in bus/people in bus_stop * 100
    if n_people_waiting is not None:
        for vehicleId in traci.vehicle.getIDList():
            if(traci.vehicle.getTypeID(vehicleId) == "b_0"):
                speed = traci.vehicle.getSpeed(vehicleId)
                if (speed > 0): #in movimento
                    next_stops = traci.vehicle.getStops(vehicleId)
                    people_in_bus =  traci.vehicle.getPersonNumber(vehicleId)
                    if(n_people_waiting != 0):
                        if(people_in_bus != 0):
                            score = (people_in_bus/n_people_waiting)*100
                            if score <= 100:
                                print("bus ", vehicleId, "score : ",score,"%")
                            else:
                                print("bus ", vehicleId, "score : 100.00%")


if __name__ == "__main__":
    # TODO: Distingue every function by line of bus
    __init__()
    i = 0
    list_people = list()
    list_people_ = list()
    while (i < 3600):
        time.sleep(0.1)# Speed of simulation
        traci.simulationStep()
        showBusBasicInfo()
        if(i%10 == 0): # after 10sec
            bus_stop_people = peopleInOut(listPeople=list_people)
            if(bus_stop_people != None):
                print("***********************************************************")
                showBusBasicInfo()
                computeScore(n_people_waiting=bus_stop_people)
        i += 1
    if(i == 3600):
        sys.exit("---> Finish simulation ")
    
