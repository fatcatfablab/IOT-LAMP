# Control your IOT lamp with MQTT. Bassed on Adafruit example code
# Peter Hartmann peter@hartmanncomputer.com

# Import standard python modules.
import random
import sys
import time
import json
import os
import subprocess
import psutil

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient


# Supply your Adafruit IO username and key as program arguments 
ADAFRUIT_IO_USERNAME = sys.argv[1] 
ADAFRUIT_IO_KEY      = sys.argv[2] 

rings_pid = 0

# Define callback functions which will be called when certain events happen.
def connected(client):
    print('Connected to Adafruit IO!')
    client.subscribe('iot-lamp.color')
    client.subscribe('iot-lamp.white')
    client.subscribe('iot-lamp.program')
    client.subscribe('iot-lamp.util')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # parse all messages
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

    if feed_id == "iot-lamp.color":
        parsed_color = json.loads(payload)
        print("red value is: %s" % parsed_color['red'])

    if feed_id == "iot-lamp.white":
        white_lights(payload)

    if feed_id == "iot-lamp.util":
        if payload == "shutdown":
            os.system("/usr/bin/sudo /sbin/shutdown -h now") 

    if feed_id == "iot-lamp.program":
        fadecandy_program(payload)

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

client.loop_background()

# the funs

def white_lights(state):
    # loop through all Dotstar pixels (we treat it the same as an RGB strip)
    for x in range(0,numpixels):
       strip.setPixelColor(x, state,state,state)
    strip.show()

def rgb_fadeto(red,blue,green):
    for i in range(numpixels):
        pixels[i] = (red, green, blue)
        client.put_pixels(pixels)
        # uncomment the second client.put_pixels for instantaneous change
#       client.put_pixels(pixels)

def fadecandy_program(prg):
    global rings_pid
    print("this is fadecandy_program, call is %s" % prg)
    print("rings_pid is %s" % str(rings_pid))
    if prg == "rings":
       print("program is rings!!")
       proc =  subprocess.Popen(["/home/pi/fadecandy/examples/cpp/rings"], shell=False, cwd="/home/pi/fadecandy/examples/cpp/",preexec_fn=os.setsid)
       rings_pid = proc.pid
       print(str(rings_pid))
    if str(prg) == "0":
       try:
          print("killing rings_pid %s" % str(rings_pid))
          kill(rings_pid)#, signal.SIGKILL)
       except:
         return str('not running')
       # loop through all fadecandy pixels
       for i in range(numpixels):
            pixels[i] = (0, 0, 0)
       client.put_pixels(pixels)
       rings_pid = 0 
       return str('200')
    print(str(rings_pid))

last = 0
while True:
       if (time.time() - last) >= 10.0:
                  last = time.time()

