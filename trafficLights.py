import os, sys, time
from requests import options
import traci
from sumolib import checkBinary
import optparse
import traci.constants as tc

'''
    Simple program that aims to show the basic information 
    about the traffic lights in the Network
'''

def __init__():
    sumoBinary = checkBinary('sumo') # sumo or sumo-gui with visual view
    sumoCmd = [sumoBinary, "-c", "oldNetwork/002.sumocfg"]
    traci.start(sumoCmd)
    print("--> Start Simulation")

def infoTrafficLights():
    '''
    Function that shows the info about the traffic light in J4 Junction 
    in the Network such as:
        -Phase number, phase description 
    '''
    #print(traci.trafficlight.getIDList())
    #print(traci.trafficlight.getAllProgramLogics("J4"))
    print("Phase n: ",traci.trafficlight.getPhase("J4"))
    print("Current Phase: ",traci.trafficlight.getRedYellowGreenState(traci.trafficlight.getIDList()[0]))
    #print(traci.trafficlight.getControlledLinks("J4"))
    #traci.trafficlight.setPhase("J4",2)

if __name__ == "__main__":
    __init__()
    i = 0
    while (i < 3600):
        time.sleep(0.1)# Speed of simulation
        traci.simulationStep()
        if(i%10 == 0): # after 10sec
            infoTrafficLights()
        i += 1
    if(i == 3600):
        sys.exit("---> Finish simulation ")