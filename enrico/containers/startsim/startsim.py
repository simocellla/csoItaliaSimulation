import traci
import os
import threading
import time
import json
from flask import Flask, request

simport = os.getenv('SIM_PORT', default = 8813)
simhost = os.getenv('SIM_HOST', default = 'localhost')
simlabel = os.getenv('SIM_LABEL', default = 'main')
webport = os.getenv('SIM_API_PORT', default = 9090)
delay = os.getenv('DELAY', default = 200)

traci.init(port=simport, host=simhost, label=simlabel)
conn = traci.getConnection(simlabel)

lock = threading.Lock()

app = Flask(__name__)

@app.route("/")
def test():
    with lock:
        l = conn.vehicle.getIDList()
        return json.dumps(l)

# secondo std rest (da vedere)
@app.route("/bus/<bus_id>", methods = ['POST'])
def add_bus(bus_id):
    # request.form['name']
    # codice per aggiungere bus nella simulazione
    return json.dumps(request.form)

@app.route("/bus/<bus_id>/<gps>", methods = ['GET'])
def get_gps(bus_id, gps):
    # request.form['name']
    # codice per aggiungere bus nella simulazione
    #ret = 
    #ret['bus_id'] = bus_id
    #ret['gps'] = 123
    return bus_id + " " + gps # json.dumps(ret)


def simulation():
    print("Starting simulation...")
    step = 0
    sim = 1
    while sim > 0:
        with lock:
            sim = traci.simulation.getMinExpectedNumber() > 0
            conn.simulationStep()
            step += 1
        if (delay - 50) > 0: time.sleep((delay - 50)/1000)
        #time.sleep(0.1)

    conn.close()

if __name__ == '__main__':
    print(delay)
    t1 = threading.Thread(target=lambda: app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()