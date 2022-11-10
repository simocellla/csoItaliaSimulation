from crypt import methods
import os
from flask import Flask, request
import requests
import time

webport = os.getenv('AMT_API_PORT', default = 9191)
app = Flask(__name__)
bus_name = 'AAAA'

# Python scemo che legge e scrive, legge dalla simulazione di noVNC, e scrive sulla nuova rete amt 

def readUpdate(bus_id=bus_name):
    # Prendere i dati da backend
    x = requests.get('http://127.0.0.1:9090/bus/'+bus_id+'/gps')
    if(x.status_code == 200):
        data = x.json()
        lat = data[0]
        lon = data[1]
        speed = data[2]
        # Inviare i dati alla rete yellow
        api_url = "http://127.0.0.1:9393/updatebus/"+bus_id#+"/"+lat+"/"+lon+"/"+speed
        todo = {"lat":lat,"lon":lon,"speed":speed}
        response = requests.post(api_url,data=todo)
        print("POST: ",response.status_code)
    else:
        return "Problem occured"

if __name__ == '__main__':
    while(1):
        readUpdate()
        time.sleep(5) # Every n_sec update the information of the bus