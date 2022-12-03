import requests
import time
import sys

'''
    init function, used to set all the info
    of the chosen bus.
'''

url_clean_bus = "http://127.0.0.1:9393/busclean/"

def __init__():
    global bus_name
    global url_clean_bus
    try:
        bus_name = str(sys.argv[1])
    except IndexError:
        print('[+] Usage: python ' + sys.argv[0] + ' <Bus ID>')
        sys.exit(0)
    bus_name = bus_name
    url_clean_bus = url_clean_bus+bus_name
    print("Bus "+bus_name+" setted")
    print("----------------------")


'''
    Function that allows to read data from the backend service
    and post the data on the yellow_team server
'''


def readUpdate():
    # GET data:
    speed_tot = 0
    url_get_ = 'http://127.0.0.1:9090/bus/'+bus_name+'/gps'
    url_get = 'http://127.0.0.1:9090/getspeed/'+bus_name+'/gps' # TODO : implementare come si deve!
    url_post = 'http://127.0.0.1:9393/updatebus/'+bus_name
    try:
        x = requests.get(url_get_)
        if(x.status_code == 200):
            data = x.json()
            lat = data[0]
            lon = data[1]
            y = requests.get(url_get)
            if(y.status_code == 200):
                data = y.json()
                speed = y.text
                print("Speed:")
                speed = data
            todo = {"lat":lat,"lon":lon,"speed":speed}
            response = requests.post(url_post,data=todo)
            if(response.status_code == 200):
                print("POST action done")
    except:
        print("[+] Connection problem!")
        todo = {"bus": bus_name}
        response = requests.post(url_clean_bus, data=todo)
        print("Before exit, cleaning:",response.status_code)
        sys.exit(0)

'''
    Main program
'''
if __name__ == '__main__':
    __init__()
    while (1):
        readUpdate()
        time.sleep(0.2)
