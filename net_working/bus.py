import requests
import time
import sys

'''
    init function, used to set all the info
    of the chosen bus.
'''    
def __init__():
    global bus_name
    name_list = sys.argv
    if(len(name_list) > 1):
        bus_name = name_list[-1]
        bus_name = bus_name
        print("Bus "+bus_name+" setted")
        print("----------------------")
    else:
        print("Please, specify a bus name (as parameter) of the program")
        sys.exit(0)


'''
    Function that allows to read data from the backend service
    and post the data on the yellow_team server
'''
def readUpdate():
    # GET data:
    url_get = 'http://127.0.0.1:9090/bus/'+bus_name+'/gps'
    url_post = 'http://127.0.0.1:9393/updatebus/'+bus_name
    x = requests.get(url_get)
    if(x.status_code == 200):
        data = x.json()
        lat = data[0]
        lon = data[1]
        speed = data[2]
        speed = sum(speed)/len(speed)
        # POST data:
        #+"/"+lat+"/"+lon+"/"+speed
        todo = {"lat":lat,"lon":lon,"speed":speed}
        response = requests.post(url_post,data=todo)
        if(response.status_code == 200):
            print("POST action done")
    else:
        print("Problem with server, try again!")
        sys.exit(0)

'''
    Main program
'''
if __name__ == '__main__':
    __init__()
    while(1):
        try:
            readUpdate()
        except:
            print("Problem with server, try again")
            sys.exit(1)
        time.sleep(5) # Every n_sec update the information of the bus