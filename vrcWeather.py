import argparse
import sys
from datetime import datetime
from _thread import *
from pythonosc import udp_client

#function to check the time of day, specifically to add or remove sunglasses
#Under Construction 
def timeOfDay():
    while True:
        localTime = datetime.now()
        client.send_message("/avatar/parameters/sunglasses",True)

    return



#Begin the OSC server
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=9000,help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

#Start the necessary threads for functions affecting avatars 
start_new_thread(timeOfDay)

#Can use this input, but really just here to maintain application running
while True:
    key_input = input("Waiting for key between -1 and 1: ")
    key_input = float(key_input)
    client.send_message("/input/Vertical", key_input)