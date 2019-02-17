# Overview

This piece of code is for broadcasting sensor data from pH sensor using Bluetooth. The sensor data is signed with a private key to produce a hash, to make sure that claims can only be validated by white-listed and authorized sensor data. For testing purposes, we specified the program to pair only the device with name "OnePlus 6T". This can be changed in `ph_bluetooth.py` with the bluetooth name of the device you wish to send the message to.

# Installation on IoT Sensor or Raspberry Pi

1. `git clone https://gitlab.doc.ic.ac.uk/avs116/sensorTRX_bluetooth.git`
2. `cd sensorTRX_bluetooth`
3. `python ph_bluetooth.py`