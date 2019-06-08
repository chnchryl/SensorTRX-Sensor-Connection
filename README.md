# Overview

This piece of code is for broadcasting sensor data from pH sensor using Bluetooth. The sensor data is signed with a private key to produce a hash, to make sure that claims can only be validated by white-listed and authorized sensor data. For testing purposes, we specified the program to pair only the device with name "OnePlus 6T". This can be changed in `ph_bluetooth.py` with the bluetooth name of the device you wish to send the message to.

# Pre-Requisites: Python Dependencies
- pygatt 
- ethereum
- web3
- pexpect

# Installation on IoT Sensor or Raspberry Pi
1. `https://github.com/chnchryl/SensorTRX-Sensor-Connection.git`
3. `cd sensorTRX_bluetooth`
4. `python ph_bluetooth.py`
