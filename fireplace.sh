#!/bin/bash

while true; do 
cat /home/pi/IOT-LAMP/fire-processing.opc |  /home/pi/openpixelcontrol/bin/opc_replay 127.0.0.1 > /dev/null 2>&1
done	
