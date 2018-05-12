#!/usr/bin/env python2
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
import signal
import opc
import atexit

# Register your external Fadecandy programs here
global ext_prgs
ext_prgs = {
        "rings":"/home/pi/fadecandy/examples/cpp/",
        "double.py":"/home/pi/IOT-LAMP/",
        }

subprocess_pid = 0

global current_prg
current_prg = "0"

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient


# Supply your Adafruit IO username and key as program arguments 
ADAFRUIT_IO_USERNAME = sys.argv[1] 
ADAFRUIT_IO_KEY      = sys.argv[2] 


from dotstar import Adafruit_DotStar
numpixels = 47 # Number of LEDs in strip

# setup fadecandy stuff.  The fadecandy server is already runing on port 7890.
# We're just telling our program where to look for it.
opc_client = opc.Client('localhost:7890')

pixels = [ (0,0,0) ] * numpixels
# Here's how to control the strip from any two GPIO pins:
datapin  = 23
clockpin = 24
# instantiate a strip object
strip = Adafruit_DotStar(numpixels, datapin, clockpin)

strip.begin()           # Initialize pins for output
#strip.setBrightness(64) # Limit brightness to ~1/4 duty cycle

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
        rgb_fadeto(parsed_color['red'],parsed_color['green'],parsed_color['blue'])

    if feed_id == "iot-lamp.white":
        white_lights(int(payload))

    if feed_id == "iot-lamp.util":
        if payload == "shutdown":
            lamp_off()
            os.system("/usr/bin/sudo /sbin/shutdown -h now") 

    if feed_id == "iot-lamp.program":
        fadecandy_program(payload)

    if feed_id == "iot-lamp.util":
        if payload == "lampoff":
            lamp_off()

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
    opc_client.put_pixels(pixels)
#    uncomment the second client.put_pixels for instantaneous change
#    opc.client.put_pixels(pixels)

def fadecandy_program(prg):
    global subprocess_pid
    global current_prg
    print("subprocess_pid is %s" % str(subprocess_pid))
    # check for running prg and change of state
    if current_prg != "0" and prg != current_prg:
        kill_prg(subprocess_pid)
    if prg in ext_prgs:
       proc =  subprocess.Popen([ext_prgs[prg]+ prg], shell=False, cwd=ext_prgs[prg],preexec_fn=os.setsid)
       subprocess_pid = proc.pid
       print("subprocess_pid is now %s" % str(subprocess_pid))
       current_prg = prg
       print("current program is %s" % str(prg))
    if str(prg) == "0":
        if subprocess_pid < 0:
            kill_prg(subprocess_pid)
            subprocess_pid = 0
        current_prg = "0"
        darken_fadecandy()

def kill_prg(pid):
   try:
      print("killing subprocess_pid %s" % str(pid))
      os.killpg(int(pid), signal.SIGTERM)
      global subprocess_pid
      subprocess_pid = 0
   except:
      pass

def darken_fadecandy():
   # loop through all fadecandy pixels
   for i in range(numpixels):
        pixels[i] = (0, 0, 0)
   opc_client.put_pixels(pixels)
   opc_client.put_pixels(pixels)

def lamp_off():
    fadecandy_program(0)
    white_lights(0)

# Turn off lamp on keybaord interrupt and service stop/restart
atexit.register(lamp_off)
signal.signal(signal.SIGTERM, lamp_off)

# hang the script so we can daemonize
last = 0
while True:
       if (time.time() - last) >= 1.0:
           # flush buffers so we get std out in our log file 
           sys.stdout.flush()
           last = time.time()

