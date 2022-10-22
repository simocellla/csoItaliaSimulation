import traci
import os
import threading
import time
import json
from flask import Flask

simport = os.getenv('port', default = 8813)
simhost = os.getenv('host', default = 'localhost')
simlabel = os.getenv('label', default = 'main')
webport = os.getenv('port', default = 9090)

traci.init(port=simport, host=simhost, label=simlabel)
conn = traci.getConnection(simlabel)

lock = threading.Lock()

app = Flask(__name__)
@app.route("/")
def test():
    with lock:
        l = conn.vehicle.getIDList()
        return json.dumps(l)

def simulation():
    print("Starting simulation...")
    step = 0
    sim = 1
    while sim > 0:
        with lock:
            sim = traci.simulation.getMinExpectedNumber() > 0
            conn.simulationStep()
            step += 1
        time.sleep(0.1)

    conn.close()

if __name__ == '__main__':
    t1 = threading.Thread(target=lambda: app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()