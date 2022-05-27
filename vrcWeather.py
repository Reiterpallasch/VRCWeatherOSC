import argparse
import requests
import time
from datetime import datetime, time
import time as t2
from _thread import *
from pythonosc import udp_client
from typing import List
from pythonosc import dispatcher
from pythonosc import osc_server

# Used variables
APIKEY = '50cabeab33746df4aef02f0a7ffb1778'
zip ='38017'
cCode = 'US'
ip = "127.0.0.1"
clientPort = 9000
serverPort = 9001

# Define OSC Client
client = udp_client.SimpleUDPClient(ip, clientPort)

def printdata(address: str, *osc_arguments: List[str]):
    print(address + "  " + str(osc_arguments[0]))

# Check time ranges
def timeBetween(begin,end,current):
    if begin < end:
        return current >= begin and current <= end
    else:
        return current >= begin or current <= end

def thunder():
    client.send_message("/avatar/parameters/thunder", True)
    client.send_message("/avatar/parameters/thunder", False)
    t2.sleep(0.5)
    client.send_message("/avatar/parameters/thunder", True)
    return

# Apply weather effects
# Under Construction - will add cloud coverage
def weatherEffects():
    while True:
        localTime = datetime.now().time()
        responseC = requests.get("https://api.openweathermap.org/data/2.5/weather?zip="+zip+","+cCode+"&appid="+APIKEY+"&units=imperial")
        cJson = responseC.json()
        cloudVal = float(cJson["clouds"]["all"])
        sky = cJson['weather']
        skyStat = sky[0]['description']
        last4 = skyStat[len(skyStat)-4:len(skyStat)]

        if (cloudVal >= float(70.0)) or (timeBetween(time(0,00),time(8,00),localTime) == True) or last4 == "rain":
            client.send_message("/avatar/parameters/removesunglasses", True)
        else:
            client.send_message("/avatar/parameters/removesunglasses", False)


        t2.sleep(1)
        print(timeBetween(time(0,00),time(8,00),localTime))
        if timeBetween(time(0,00),time(8,00),localTime) == True and last4 != "rain":
            client.send_message("/avatar/parameters/hat", True)
            client.send_message("/avatar/parameters/rain", True)
            client.send_message("/avatar/parameters/thunder", True)
        else:
            client.send_message("/avatar/parameters/hat", False)
            client.send_message("/avatar/parameters/rain", False)
            thunder()

        t2.sleep(15)
    return
        
# Get the temperature - Will send a float to affect your avatar based on temperature
# I have not figured out quite yet how to determine if to use F or C - wont matter once normalized (matters now) plus can change request url to metric with
# &units=metric instead of &units=imperial
# Used for temperature based effects
def getTemp():

    responseT = requests.get("https://api.openweathermap.org/data/2.5/weather?zip="+zip+","+cCode+"&appid="+APIKEY+"&units=imperial")
    tJson = responseT.json()
    tempuratureVal = float(tJson["main"]["temp"])
    return tempuratureVal

# Begin the OSC server
def server(dispatcher):
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/avatar/parameters/*", printdata)

    server = osc_server.ThreadingOSCUDPServer((ip, serverPort), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

# Apply Temperature effects
def tempEffects():
    while True:
        temperatureVal = getTemp()
        temperatureValNormal = float(temperatureVal/100)

        if temperatureValNormal >= 1:
            temperatureValNormal = .99

        if temperatureValNormal >= .75:
            client.send_message("/avatar/parameters/skinTone",temperatureValNormal)
        else:
            client.send_message("/avatar/parameters/skinTone",0.00)

        if(temperatureVal > float(82.0)):
            client.send_message("/avatar/parameters/sweat",True)
        else:
            client.send_message("/avatar/parameters/sweat",False)

        t2.sleep(30)
    return

# Start the necessary threads for functions affecting avatars 
start_new_thread(weatherEffects,())
start_new_thread(tempEffects,())
start_new_thread(server(dispatcher),())

# Can use this input, but really just here to maintain application running
# while True:
#     key_input1 = input("Type q and press enter to close: ")
#     # key_input = input("Waiting for key between -1 and 1: ")
#     # key_input = float(key_input)
#     # client.send_message("/input/Vertical", key_input)
#     if key_input1 == "q":
#         break