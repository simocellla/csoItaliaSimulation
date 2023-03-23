import requests
import time
import sys

#url_post = 'http://127.0.0.1:9393/updatebus/'
#url_clean_bus = "http://127.0.0.1:9393/busclean/"

url_post = 'http://10.254.254.101:5000/updatebus/'
url_clean_bus = 'http://10.254.254.101:5000/busclean/'

speed = 0
bus_name = None

def __init__():
    global speed
    global url_post
    global url_clean_bus
    global speed
    global bus_name
    try:
        bus_name,speed = str(sys.argv[1]), sys.argv[2]
        url_post = url_post+bus_name
        url_clean_bus = url_clean_bus+bus_name
    except IndexError:
        print('[+] Usage: python ' + sys.argv[0] + ' <Bus ID> <desidered speed>')
        sys.exit(0)
    print("         Bus "+bus_name+"\n"+"Desidered speed injection:",speed)
    print("------------------------------")


def injection():
    lat = 0
    lon = 0
    try:
        for i in range(0,30):
            todo = {"lat": lat, "lon": lon, "speed": speed,"id":bus_name}
            response = requests.post(url_post, data=todo)
            print(todo)
            print(f"iteration",i,": ",response)
            time.sleep(0.1)
            if(i == 29):
                todo = {"bus": bus_name}
                response = requests.post(url_clean_bus, data=todo)
                print("Before exit",response.status_code)
    except:
        print("[+] Connection problem!")
        sys.exit(0)


'''
    Main program
'''
if __name__ == '__main__':
    __init__()
    injection()
    time.sleep(0.5)