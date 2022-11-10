import os
import json
from flask import Flask, request
import requests
#webport = os.getenv('SIM_API_PORT', default = 9090)

webport = os.getenv('AMT_API_PORT', default = 9292)
app = Flask(__name__)

'''
    Primary route, this will get the name of all the 
    vehicles in the Simulation
'''

def test():
    x = requests.get("http://127.0.0.1:9090/")
    print(x.status_code)


@app.route("/palina/<palina_id>/<bus_id>", methods=['GET'])
def showPalina(palina_id,bus_id):
    time = 10 # TODO implement the correct value retrieval
    if (palina_id is not None and bus_id is not None):
        if(any(bus_id in x for x in bus_added)):
            if (len(timetable) > 0):
                for time in timetable:
                    if(time['bus'] == bus_id):
                        if(palina_id in time['time']):
                            time = (10*(time['time'].index(palina_id) +1))
                            out = "Bus "+bus_id+" is arriving in "+str(time)+" min at "+palina_id+" "
                            people = next(v['people_waiting'] for v in fermate_tot if v['id'] == palina_id)
                            return out+" ,"+str(people)+" people are waiting on it"
                        else: return "Error with input"
            else: return "Error with input"
        else: return "Error with input"
    else: return "Error with input"


if __name__ == '__main__':
    while(1):
        app.run(port=webport, host='0.0.0.0', debug=True, use_reloader=False)
        test()