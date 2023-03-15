
# Cyber Range scenario based on Digital Twin for the local public transport in the city of Genoa (Italy)

## Table of contents
* [General info](#general-info)
* [Technologies used](#technologies-used)
* [Setup](#setup)
* [Digital Twin Composition](#dt)
* [Implemented Scenario](#scenario)
* [Default Configuration](#configuration)
* [Dashboards and metrics](#dashboards)
* [Attacker's point of view](#attacker)
* [Consequences of the attack in the network](#consequences)

## General info
This work contributes to the development of a more secure public transportation system
by providing a framework for creating and evaluating cybersecurity scenarios in a safe and
controlled environment, as well as an innovative approach to cyber training that improves
users’ ability to recognize and respond to threats.

## Technologies used
Python3 - https://www.python.org/  <br/>
Sumo 1.14.1 - https://sumo.dlr.de/docs/index.html <br/>
Traci 1.14.1 - https://pypi.org/project/traci/ <br/>
Podman 4.3 - https://podman.io/ <br/>
Flask 2.2.x - https://flask.palletsprojects.com/en/2.2.x/ <br/>
Prometheus 2.43 - https://prometheus.io/ <br/>
Grafana 9.3.6 - https://grafana.com/ <br/>
noVNC 1.4.0 - https://novnc.com/info.html <br/>

## Setup
In order to use the Cyber Range, it is necessary to install the applications shown in Technologies used.
The work was developed through virtualization logic in containers, which can be easily seen in ([containers dir](enrico/containers)), all orchestrated by Podman.

After installing the required applications, simply move to the containers directory, and with administrator privileges launch the command 
```console
root@machine:/home/machine/Desktop/csoItaliaSimulation/NAME/containers# make
```
with the *make* command, the Makefile will take care of creating all the containers required for the simula
Similarly, one must point to the scenario/csoItalia directory in order to start the simulation. 

Once the environment has been created, it will be possible to interact with it, as shown next.

## Digital Twin Composition
### Simulation environment
In order to create the scenario under consideration, a mobility simulator, SUMO was chosen for this purpose.
Once the maps were exported in OSM format, and converted to XML to give them to SUMO, the network looks as follows: 

![](net_working/fig/sumoView.jpg?raw=true "Sumo view")

The stretch of road connecting Corso Guglielmo Marconi and Corso Italia in Genoa was used as a simulation environment.

### Composition of the Networks
Podman was used to create the Networks part; the sketch of the networks, as set up in the implemented scenario, can be seen in the figure presented below.

![](net_working/fig/NetSketch.jpg?raw=true "Networks sketch")

As can be seen, four main networks were created:
- AMT proprietary control center network [chosen address: http://10.254.254.101:5000]
- Management network [chosen address: http://10.254.254.100:9090]
- Simint network [chosen address: http://3.3.0.0]
- Municipality network [chosen address: http://2.2.2.2]

Once both the simulation environment and the orchestration of the networks have been created, the user is ready to use the cyber range that has been developed.



## Implemented Scenario
We decided to replicate the real-life situation of a group of passengers, who need to move from the beginning of Corso Marconi, to get to the end of Corso Italia.

To make this trip, the group of people decided to use public transportation.
The best option is undoubtedly to take the bus in Corso Marconi 1, which will take the passengers to the end of Corso Italia, precisely to Corso Italia3-Zara bus stop.

Specifically, the group of people will use the bus of line 31, which can take them to their destination every 15minutes.

The flow of the trip can be described by the figure below:

![](net_working/fig/scenario.jpg?raw=true "Scenario people's flow")

As can be seen in order to decide which Bus to take passengers will choose to use the smart displays that can be found at each bus stop.
There are 5 smart displays implemented for this Cyber Range:

- Marconi1-Fiera
- Marconi2-Rimessa
- Italia1-PuntaVagno
- Italia2-Piave
- Italia3-Zara

Each of these smart displays has been implemented through a Pod that will contain its own logic; each of these Pods will aim to show on the screen the average arrival time of buses that have been scheduled for that particular route.

## Default Configuration

By default, the scenario setup has two buses, A1 and A2, in the simulation, which will be part of the simulation until it is stopped.

Furthermore, the way the scenario implementation was decided will generate a flow of 120people per hour, who will go to wait for the arrival of the first bus at the Marconi1-Fiera stop, and then get off after four stops at Italia3-Zara

#### Changing configuration

In order to change the configuration to your liking, there are two paths you can take:
- The first, by editing the .xml files that sumo needs in order to run the simulation
- The second, interacting thanks to the API made available with Flask.
Thanks to these APIs it will be possible to add buses and check their status by making calls (GET/POST) to the chosen network.


## Dashboard and Metrics

Two custom dashboards that have been implemented for our cyber domain.
These dashboards are designed to provide valuable information and situational awareness for both the blue team defenders and the white team orchestrators of the scenario.

The **Situation Awareness** dashboard is tailored to the blue team and provides a comprehensive view of the current state of the cyber domain, including real-time monitoring of network traffic, system activity, and user behavior.

The **White Team View** dashboard, on the other hand, is designed specifically for the white team and provides a comprehensive view of the cyber domain, including information on targets, and graphs to recognize vulnerabilities and potential attack vectors.

Together, these dashboards provide cyber range operators and participants with a powerful set of tools to quickly identify potential threats, assess their impact, and proactively respond to protect critical assets.

All these data visualization processes were developed through the technologies of Prometheus and Grafana.

A graphical view of the appearance of the two designed dashboard could be seen below:

Situation Awareness Dashboard:
![](net_working/fig/situationAwareness.jpg?raw=true "Situation Awareness")

<br><br>
White Team View Dashboard:
![](net_working/fig/whiteTeamView.jpg?raw=true "White Team View")

## Attacker's point of view

It is assumed that the attacker has managed to locate the APIs that the company uses to integrate assets into the urban infrastructure; in particular, it is assumed that the attacker has managed to find unprotected API calls and use them for his purposes.

Since the attacker’s main goal in this context is to introduce disorder into the passenger information network, which consists of smart displays placed at each bus stop, it is assumed that the attacker was initially able to learn the bus’s write requests and use his knowledge to transmit its own information to the control center with inconsistent data. 

This was replicated with a script in Python, the so called [injection_speed.py](net_working/injection_speed.py). Intuitively, once the script is run, the attacker is able to send inconsistent data to the AMT exposed API, which propagates this erroneous information throughout the network and triggers a cascading effect that spreads to the smart displays at bus stops.

## Consequences of the attack in the network

Due to the configuration of the network, the consequences of the incident are not limited to the integrity of the specific smart display.
The effect of such an attack could potentially propagate throughout the network, but since the attacker has exploited the sending of inconsistent data to the AMT exposed API regarding the bus itself, this effect will spill over to all other stops in the network, rendering the entire ecosystem of the smart displays of this route inconsistent.