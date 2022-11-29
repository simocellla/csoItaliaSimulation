import requests
import sys
import time

global url_get
global palina_id
global url_time
global fermate

url_get = "http://127.0.0.1:9393/palina/"
url_time = "http://127.0.0.1:9393/getime"
fermate  = ["Marconi1-Fiera","Marconi2-Rimessa","Italia1-PuntaVagno","Italia2-Piave","Italia3-Zara"]


'''
    Init function, used to set all the info
    of the smart-display
'''
def __init__():
    global palina_id
    global fermate
    name_list = sys.argv
    if(len(name_list) > 1):
        palina = name_list[-1]
        if(palina in fermate):
            palina_id = palina
            print("Palina "+palina_id+" setted")
            print("---------------------------")
        else:
            print("Please, Provide a correct name!")
            sys.exit(0)
    else:
        print("Please, provide (as parameter) the name of the smart-display")
        sys.exit(0)
    

'''
    Function that allows to read data from the backend service
    and print the data on its smart screen (palina)

    :param palina_id: str, name of the palina that we want to use
'''
def readAllUpdate(palina_id):
    time = requests.get(url_time)
    x = requests.get(url_get+palina_id)
    if(x.status_code == 200): 
        print("Time:",time.text)
        if(x.text != "Error"):
            if(len(x.json()) > 0):
                print(x.json())
        else:
            print("      No Bus scheduled"+
            "\n"+"---------------------------")


if __name__ == '__main__':
    __init__()
    while(1):
        try:
            readAllUpdate(palina_id=palina_id)
        except:
            print("Error with server!")
            sys.exit(1)
        time.sleep(1) # Every n_sec update the information of the palina