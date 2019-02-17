#coding: utf-8
import pygatt
import logging
import time
import random
import smbus
from pygatt.util import uuid16_to_uuid
from pygatt.exceptions import NotConnectedError, NotificationTimeout
from ph_sensor import AtlasI2C
from ph_claim_data import *
from data_chunker import *
from hash_sensor_value import get_signed_data
import math
import re

# Log configuration
logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

global flag
flag = 0

# List of the adapters there are trying to connect to Bluetooth.
adapters = []

# List of devices.
devices = []

# List of data of the devices to show for user (connected number and MAC).
connected_devices_list = []

# Characteristic to receive data.
uuid_received_data = uuid16_to_uuid(0x0000)    
# Characteristic to sent data.    
uuid_sent_data = uuid16_to_uuid(0x0003)    
# Characteristic used to receive the name of the application.        
uuid_bluetooth_mac = uuid16_to_uuid(0x0004)        

def get_light_sensor_value():
    bus = smbus.SMBus(1)
    time.sleep(1)
    bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
    bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)
    time.sleep(1)
    data_visible = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
    data_infrared = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)
    # conver the data
    value_visible = data_visible[1] * 256 + data_visible[0]
    value_infrared = data_infrared[1] * 256 + data_infrared[0]
    print("light value is: " + str(value_visible))
    return value_visible

def get_ph_sensor_value():
    ph_sensor = AtlasI2C()
    sensor_response = ph_sensor.query("R")
    sensor_value = re.findall(r"[-+]?\d*\.\d+|\d+", sensor_response)
    time.sleep(1)
    return sensor_value

def callback(handle, data):
    
    # The callback function is called just when the characteristic to sent data is subscribed. 
    print ("Received data: " + str(data))
    # Sending "exit" string from any connected device, the python program will be closed, 
    # setting the flag. 
    if str(data) == "exit":
        global flag
        flag = 1
    answer = str(data)
    try:
        s =  str(data)    
        data = answer.encode()
        data = data[:2] + ": ".encode() + data[2:]
        # Interpretation of the communication protocol between App and DB:
        
        # If the first two digits received from Dragonboard are DB, 
        # the board will send the string to all connected devices.
        #if s[:2]  == 'DB':
        for device in devices:
            device.char_write(uuid_sent_data, data, False) 
                
        # If the first digits received from Dragonboard are "D" followed by a number less than number of connected devices, 
        # the board will send the string to the device corresponding to that number.
        # elif s[0] == 'D' and s[1].isdigit() and int(s[1])<len(devices):
        
        
       # devices[int(s[1])].char_write(uuid_sent_data, data, False)   
        
        # If there is no prefix on the received data, the string is just received on Dragonboard.
    except NotificationTimeout as e:
        print (e)
 
# Function to connect to device.           
def connect_to_device (adapter, MAC):
        connected = 0
        timeout = 5
    
        adapter.clear_bond(MAC)
        adapter.start(False)
        try:
            # The program tries to connect to random MAC Bluetooth 
            # (normally used on Android 6 or higher).
            # In this case, the pygatt.BLEAddressType.random parameter is used in the connect function.
            print ("Random MAC connection")
            device = adapter.connect(MAC, timeout, pygatt.BLEAddressType.random)
            connected = 1
        except NotConnectedError:
         
            print ("NotConnectedError.message")
            return ("", connected)

        if connected == 1:
            try:
                # If the connection is established with any device, characteristics are discovered
                # and using subscribe function is initiated the communication between application and Dragonboard,
        	# waiting for a message of the application.
                device.discover_characteristics()
                device.subscribe(uuid_sent_data, indication = False)
                device.subscribe(uuid_received_data, callback, False)
                device.subscribe(uuid_bluetooth_mac, indication = False)
    
                return (device, connected)

            except pygatt.exceptions.BLEError:
                connected = 0
                return ("", connected)                        

def get_claim_data(sensor_value, time):
    claim_data_dict = get_signed_data(sensor_value, time)

    #v, r, s, msgHash, value, time, signer
    return ClaimData(claim_data_dict['v'], claim_data_dict['r'], claim_data_dict['s'],\
                     claim_data_dict['msgHash'], claim_data_dict['time'], sensor_value,\
                     claim_data_dict['signer'])
        
try:   
    # scan_adapter it's a scan used to list all founded devices.    
    scan_adapter = pygatt.GATTToolBackend(search_window_size=400)
    scan_adapter.start()
    ble_devices = scan_adapter.scan(timeout = 10, run_as_root = True)
    
    scan_adapter.stop()
    
    # If the program doesn't find any bluetooth device, the program will be closed, 
    # setting the flag.    
    if ble_devices == []:
        print ("\nScan didn't find any devices. Finishing program.")
        flag = 1
    cont = 0
    
    # Prints all devices founded by scan on Dragonboard
    
    my_ble_device = []
    for ble_device in ble_devices:
        cont = cont + 1
        print (str(cont) + "- " + str(ble_device['name']) + ": " + str(ble_device['address']))     
        
        if (ble_device['name'] == "OnePlus 6T"):
            my_ble_device.append(ble_device)

    ble_devices = my_ble_device
    print(ble_devices)
    
    # All adapters are initialized before the connection is established.      
    for i in range(0, len(ble_devices)):
        adapters.append(pygatt.GATTToolBackend())
        time.sleep(1)
    time.sleep(1)
            
    # Connects with all devices that are with opened application.
    cont = 0    
    i = 0
    for device in ble_devices:
        print("\nConnecting to: " + device['address'])
        d = connect_to_device(adapters[cont], device['address'])
        if d[1] == 1:
            # List with dictionary including data that will send to application.
            connected_device = {'number':i,'address':device['address']}
            connected_devices_list.append(connected_device)
            i = i + 1
            devices.append(d[0])
        cont = cont + 1 
        time.sleep(2)
    print ("Connection to devices finished.\n")

    # Shows a list of connected devices with each number used in the communication protocol. 
    for i in connected_devices_list:
        print ("D"+str(i['number'])+"- "+i['address'])
    print ("\n")
                
    # If none connection was established, the program will be closed,
    # setting the flag.
    if devices == []:
        print ("\nNo connection to devices. Finishing program.")
        flag = 1

    # Sends to application a list of connected devices.
    #for device in devices:
    #    print (device)
    #    s = "Device list: "
    #    device.char_write(uuid_sent_data, s.encode(), False)    
        
    #for connected_device in connected_devices_list:
    #    s = "D" + str(connected_device["number"]) +":" + str(connected_device["address"])
    #    data = s.encode()
    #    for device in devices:
    #        device.char_write(uuid_sent_data, data, False)

    while True:
        sensor_measurement = get_ph_sensor_value()
        for device in devices:

            print("DEBG SENSOR MEAS", type(sensor_measurement[0]))

            meas_time = int(time.time() * 1000)
            claim_data = get_claim_data(float(sensor_measurement[0]), meas_time)
            claim_str = claim_data.generate_string()

            data_chunker = DataChunker(claim_str)
            claim_tokens = data_chunker.generate_token_list()

            print("CLAIM DATA GENERATE: " + claim_str)
            
            for claim_token in claim_tokens:
                device.char_write(uuid_sent_data, claim_token.encode(), False) 
            
            time.sleep(1)

except NotConnectedError:
    print ("NotConnectedError.message")
  
finally:
    # Structure to maintain the python program opened, waiting for a message coming from callback function.

    while True:   
        # Stops all adapter, and close python program when the flag is setted.
        if flag == 1:
            scan_adapter.stop()
            for adapter in adapters:   
                adapter.stop()
            break
