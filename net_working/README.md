# Run NET simulation

## Run the enviroment:

As ```root```, execute ```make``` in the ```containers``` directory to build the images.

As ```root```, execute ```make``` in the ```scenarios/test/``` directory to run the test scenario.

As ```normal user```, execute ```startsim_backend.py``` 

As ```normal user```, execute ```startsim_yellow.py```

Make a ```POST``` request in this form : 
```curl -X POST 127.0.0.1:9090/busflow/AAAA```

As ```normal user```, execute ```bus.py```

## Output View:
You can access the ```sumo-gui``` with a web browser opening the url [http://127.0.0.1:9999](http://127.0.0.1:9999) and a test REST api opening the url [http://127.0.0.1:9090](http://127.0.0.1:9090)

To stop the simulation, execute ```make stop``` in the ```scenarios/test/``` directory.
