# SUMO PoC with pods and containers

## Requirements

It requires podman > v.4.0

## Run the PoC

As ```root```, execute ```make``` in the ```containers``` directory to build the images.

As ```root```, execute ```make``` in the ```scenarios/csoItalia``` directory to run the test scenario.

To stop the simulation, execute ```make stop``` in the ```scenarios/csoItalia``` directory.

## Test of the PoC

To test if the environment has been correctly set there are several ways, the fastest is to reach the hello world page of the backend network, reaching the address : ```http://10.254.254.100:9090/environment``` , if it will answer us with ```{'type':Startsim_Backend}```, it means that the simulation is running correctly.

## Add new bus pod to the simulation

To add a new bus in the simulation, is necessary to add a new pod to the simulation environment.
In order to do this, is necessary to modify the [Makefile](scenarios/csoItalia/Makefile) file, and add something like:
```Makefile
...
BUS_name=<name>
...
	# Bus <name>
	PODNAME=bus<name> \
	ETH0_NET=mgmt-crltp \
	ETH0_IP=10.254.254.10x \
	ETH1_NET=simint-crltp \
	ETH1_IP=3.3.0.x \
	BUS_name=$(BUS_name) \
	PYTHONUNBUFFERED=1 \
	$(MAKE) -C ../../pods/bus/ start
```
Where in ```ETH0_IP``` and ```ETH1_IP``` value need to be different than the others already in the [Makefile](scenarios/csoItalia/Makefile).

### Last step

Now that the pod has been set up when the simulation starts it will begin to run, but only when the POST action to the backend system (```/bus/<name>``` or ```/busflow/<name>``` call) is done will it be possible to see it in the simulation.