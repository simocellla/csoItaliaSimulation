from crypt import methods
import os
from flask import Flask, request
import requests
import time


palina_id = "Italia2-Piave"

# Python scemo che legge 
def readUpdate(palina_id=palina_id):
    # Prendere i dati da backend
    x = requests.get('http://127.0.0.1:9393/printpalina/'+palina_id)
    if(x.status_code == 200): 
        data = x.json()
        print(data)
    else:
        print("No Bus")

def readAllUpdate(palina_id):
    x = requests.get("http://127.0.0.1:9393/palina/"+palina_id)
    if(x.status_code == 200): 
        data = x.json()
        if(len(data) > 0):
            print(data)
        else:
            print("No Bus scheduled")
    else:
        print("No Bus")

if __name__ == '__main__':
    while(1):
        #readUpdate()
        readAllUpdate(palina_id=palina_id)
        time.sleep(1) # Every n_sec update the information of the bus