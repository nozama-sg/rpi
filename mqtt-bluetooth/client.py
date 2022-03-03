import paho.mqtt.client as paho
import sys
import time
import json
import requests
import userpass

mqttServerIP = 'localhost'
# mqttServerIP = '192.168.1.104'

userId = "darentan"
deviceName = 'iBeacon:c80c71ef-1086-4601-9dc1-c83eadb4be7c-0-0'
bluetoothUpdateURL = "http://119.13.104.214:80/locationUpdate"
updateDelayTime = 60

valuesDict = {}

def onMessage(client, userdata, message):
    baseStation = message.topic.split('/')[-1]
    message = json.loads(message.payload.decode())
    deviceId = message['id']
    rssi = message['rssi']
    mac = message['mac']

    print(f"LOG: {baseStation}:{deviceId} | RSSI: {rssi} | MAC: {mac}")

    # we can incorporate the deviceId to enable multiple watch support
    valuesDict[baseStation] = rssi
    print(valuesDict)

    # get key in valuesDict with highest value
    maxBaseStation = max(valuesDict, key=valuesDict.get)
    print(maxBaseStation)
    
    data = {
        "userId": userId,
        "roomName": maxBaseStation,
    }

    response = requests.post(bluetoothUpdateURL, json=data)

    if response.status_code != 200:
        print(f"ERROR: {response.status_code} | {response.text}")

    time.sleep(updateDelayTime)
    
def onLog(client, userdata, level, buf):
    print(f"LOG: {buf}")

client = paho.Client("RPi Client")
client.username_pw_set(userpass.user, userpass.password)
client.on_message = onMessage
# client.on_log = onLog

if client.connect(mqttServerIP, 1883) != 0:
    print("Could not connect to MQTT Broker")
    sys.exit(-1)

client.subscribe(f"espresense/devices/{deviceName}/#")

try:
    print("Press CTRL+C to exit....")
    client.loop_forever()
except:
    print("Disconnecting from broker")

client.disconnect()
