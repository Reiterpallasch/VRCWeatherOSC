import argparse
import sys
import pyowm
import requests
import time
#from pyowm.owm import OWM
from datetime import datetime, time
import time as t2
from _thread import *
from pythonosc import udp_client
from typing import List
from pythonosc import dispatcher
from pythonosc import osc_server


APIKEY = '50cabeab33746df4aef02f0a7ffb1778'
zip ='38017'
cCode = 'US'

#broken? resorting to normal api calls
# OpenWMap=pyowm.OWM(APIKEY)
# Weather = OpenWMap.weather_at_place('Collierville')
# Data=Weather.get_weather()
# temp = Data.get_temperature(unit='fahrenheit')

#Tesing Responses
# response = requests.get("https://api.openweathermap.org/data/2.5/weather?zip="+zip+","+cCode+"&appid="+APIKEY+"&units=imperial")
# print(response.json())
# respJson = response.json()
# tempurature = respJson["main"]
# print(tempurature["temp"])

def printdata(address: str, *osc_arguments: List[str]):
    print(address + "  " + str(osc_arguments[0]))

#Check time ranges
def timeBetween(begin,end,current):
    if begin < end:
        return current >= begin and current <= end
    else:
        return current >= begin or current <= end


#function to check the time of day, specifically to add or remove sunglasses
#Under Construction - will add cloud coverage
def timeOfDay():
    while True:
        localTime = datetime.now().time()
        responseC = requests.get("https://api.openweathermap.org/data/2.5/weather?zip="+zip+","+cCode+"&appid="+APIKEY+"&units=imperial")
        cJson = responseC.json()
        cloudVal = float(cJson["clouds"]["all"])
        if (cloudVal >= float(70.0)) or timeBetween(time(0,00),time(8,00),localTime) == True:
            client.send_message("/avatar/parameters/removesunglasses",True)
        else:
            client.send_message("/avatar/parameters/removesunglasses",False)
        #Printing to see if server and client may exist simultaneously
        print("Success")
        t2.sleep(15)
    return
        


#Get the temperature - Will send a float to affect your avatar based on temperature
#I have not figured out quite yet how to determine if to use F or C - wont matter once normalized (matters now) plus can change request url to metric with
# &units=metric instead of &units=imperial
def getTemp():
    while True:
        responseT = requests.get("https://api.openweathermap.org/data/2.5/weather?zip="+zip+","+cCode+"&appid="+APIKEY+"&units=imperial")
        tJson = responseT.json()
        tempuratureVal = float(tJson["main"]["temp"])
        tempuratureValNormal = float(tempuratureVal/100)
        if tempuratureValNormal >= 1:
            tempuratureValNormal = .99
        if tempuratureValNormal >= .75:
            client.send_message("/avatar/parameters/skinTone",tempuratureValNormal)
        else:
            client.send_message("/avatar/parameters/skinTone",0.00)
        if(tempuratureVal > float(82.0)):
            client.send_message("/avatar/parameters/sweat",True)
        else:
            client.send_message("/avatar/parameters/sweat",False)
        t2.sleep(30)
    return

#Begin the OSC server
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=9000,help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

#Start the necessary threads for functions affecting avatars 
start_new_thread(timeOfDay,())
start_new_thread(getTemp,())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9001, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/*", printdata)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

#Some sqlite error going on here
# owm = OWM('50cabeab33746df4aef02f0a7ffb1778')
# reg = owm.city_id_registry()
# list_of_tuples = reg.ids_for('Memphis', matching='exact')
# print(list_of_tuples)

#Can use this input, but really just here to maintain application running
while True:
    key_input1 = input("Type q and press enter to close: ")
    # key_input = input("Waiting for key between -1 and 1: ")
    # key_input = float(key_input)
    # client.send_message("/input/Vertical", key_input)
    if key_input1 == "q":
        break