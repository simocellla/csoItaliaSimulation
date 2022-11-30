# Run NET simulation
## Rapid description of the net

```localhost:9090``` : backend network <br />
```localhost:9393``` : yellow_team network <br />
```localhost:9999``` : sumo-gui/graphical view of the scenario <br />

## Scenario design of networks

<img src="https://github.com/simocellla/csoItaliaSimulation/blob/main/net_working/fig/scenario_view.png" width="400" height="410">

## Run the enviroment

As ```root```, execute ```make``` in the ```containers``` directory to build the images.

As ```root```, execute ```make``` in the ```scenarios/csoItalia/``` directory to run the test scenario.

---

As ```normal user```, execute ```startsim_backend.py``` *this will be the BACKEND network of AMT*

As ```normal user```, execute ```startsim_yellow.py``` *this will be the YELLOW_TEAM network of AMT*

---

Make a ```POST``` request (in order to add a bus in the net) with this form : <br />
```curl -X POST 127.0.0.1:9090/busflow/AAAA```
this will add a bus 'AAAA' in the net (will be useful for interacting with the next program)

---

As ```normal user```, execute ```bus.py``` <br />
example of execution : ```python3 bus.py AAAA```

As ```normal user```, execute ```palina.py```<br />
example of execution : ```python3 palina.py Italia3-Zara```

---

```n.b:``` both, ```bus.py``` and  ```palina.py``` are built for specific entity in the network, this means that you have to specify both the name of the bus and the name of the palina as parameter of desidered program in python.

## Output View
You can access the ```sumo-gui``` with a web browser opening the url [http://127.0.0.1:9999](http://127.0.0.1:9999) and a test REST api opening the url [http://127.0.0.1:9090](http://127.0.0.1:9090) <br />

Also you can perform some GET requests, to new added ```yellow_network``` by typing on the browser : [http://127.0.0.1:9393/bus/AAAA](http://127.0.0.1:9393/bus/AAAA) <br />

---

To **stop** the simulation, execute ```make stop``` in the ```scenarios/test/``` directory. <br />