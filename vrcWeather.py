import argparse
from asyncio.windows_events import NULL
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

# Flag to later be used with listening server to apply breath effects on certain visemes
class flags(object):
    hotFlag = False
    coldFlag = False

flagSet = flags()
# Define OSC Client
client = udp_client.SimpleUDPClient(ip, clientPort)

def printdata(address: str, *osc_arguments: List[str]):
    print(address + "  " + str(osc_arguments[0]))
    # Respond to specific outputs i.e. to get breath effects when talking (in progress)
    if (address + "  " + str(osc_arguments[0])) == "/avatar/parameters/Viseme  0" or (address + "  " + str(osc_arguments[0])) == "/avatar/parameters/Viseme  1":
        print("found")
        if flagSet.coldFlag == True:
            print("Damn it's cold")
        elif flagSet.hotFlag == True:
            print("Damn it's hot")

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
        last4 = ""
        if len(sky) > 1:
            skyStat = sky[1]['description']
            last4 = skyStat[len(skyStat)-4:len(skyStat)]
        #print(last4)
        # Remove sunglasses
        if (cloudVal >= float(70.0)) or (timeBetween(time(0,00),time(8,00),localTime) == True) or last4 == "rain":
            client.send_message("/avatar/parameters/removesunglasses", True)
        else:
            client.send_message("/avatar/parameters/removesunglasses", False)


        t2.sleep(.5)
        # Sanity check print
        #print(timeBetween(time(0,00),time(8,00),localTime))

        # Remove hat
        if timeBetween(time(0,00),time(8,00),localTime) == True and str(last4) != "rain":
            client.send_message("/avatar/parameters/hat", True)
            client.send_message("/avatar/parameters/rain", True)
            client.send_message("/avatar/parameters/thunder", True)
        else:
            client.send_message("/avatar/parameters/hat", False)
            if str(last4) == "rain":
                client.send_message("/avatar/parameters/rain", False)
                thunder()
            else:
                client.send_message("/avatar/parameters/rain", True)

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
        if temperatureVal > 100:
            temperatureVal = 100

        temperatureValNormal = float(temperatureVal/100)

        # Start skin tone at a certain temp
        # Hot
        if temperatureValNormal >= .75:
            flagSet.hotFlag = True
            flagSet.coldFlag = False
            client.send_message("/avatar/parameters/skinTone2",0.00)
            tempHot = float((temperatureValNormal - .75)/(1 - .75))
            # Radial resets at 100?
            if tempHot >= 1:
                tempHot = .99
            client.send_message("/avatar/parameters/skinTone",tempHot)
        #Cold
        elif temperatureValNormal <= .55:
            flagSet.coldFlag = True
            flagSet.hotFlag = False
            client.send_message("/avatar/parameters/skinTone",0.00)
            # Need to invert values to handle positive radial
            tVNInverse = 1 - temperatureValNormal
            tempCold = float((tVNInverse - .45)/(1 - .45))
            client.send_message("/avatar/parameters/skinTone2",tempCold)
        else:
            flagSet.hotFlag = False
            flagSet.coldFlag = False
            client.send_message("/avatar/parameters/skinTone",0.00)
            client.send_message("/avatar/parameters/skinTone2",0.00)
        # Sweat above a certain value
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