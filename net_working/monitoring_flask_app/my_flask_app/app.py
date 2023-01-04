import logging
import traci
import os 
import threading

from flask import Flask
from flask import jsonify,request
from prometheus_flask_exporter import PrometheusMetrics

logging.basicConfig(level=logging.INFO)
api = Flask(__name__)
metrics = PrometheusMetrics(api)

metrics.info("app_info", "App Info, this can be anything you want", version="1.0.0")

simport = os.getenv('SIM_PORT', default=8813)
simhost = os.getenv('SIM_HOST', default='localhost')
simlabel = os.getenv('SIM_LABEL', default='main')
webport = os.getenv('SIM_API_PORT', default=9090)
delay = os.getenv('DELAY', default=100)

traci.init(port=simport, host=simhost, label=simlabel)
conn = traci.getConnection(simlabel)

lock = threading.Lock()

# Global Vars:


'''
    Main program:
'''
def simulation():
    global step
    global list_vehicle
    print("Starting simulation...")
    step = 0
    sim = 1
    list_vehicle = traci.vehicle.getIDList()
    while sim > 0:
        with lock:
            sim = traci.simulation.getMinExpectedNumber() > 0
            conn.simulationStep()
            step += 1
    conn.close()

'''
    Main program
'''
if __name__ == '__main__':
    print("Setted delay: ",delay)
    # t1 = threading.Thread(target=lambda: api.run(port=webport, host='1.1.1.1', debug=True, use_reloader=False)).start()
    t2 = threading.Thread(target=simulation()).start()

