# Sumo PoC with pods and containers

## Requirements

It requires podman v.4.0.

## Run the PoC

As ```root```, execute ```make``` in the ```containers``` directory to build the images.

As ```root```, execute ```make``` in the ```scenarios/test/``` directory to run the test scenario.

You can access the ```sumo-gui``` with a web browser opening the url [http://127.0.0.1:9999](http://127.0.0.1:9999) and a test REST api opening the url [http://127.0.0.1:9090](http://127.0.0.1:9090)

To stop the simulation, execute ```make stop``` in the ```scenarios/test/``` directory.