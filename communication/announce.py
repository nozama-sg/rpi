import flask
import subprocess
import time
import os
import requests
import pyttsx3

userId = "15"
endpointUpdateURL = 'http://119.13.104.214:80/announcementEndpointUpdate'

# creating tunnel endpoint
print("Creating Tunnel")

p = subprocess.Popen(['node', 'tunnel/tunnel.js'])
while os.path.exists('tunnelURL.txt') == False:
    time.sleep(1)
with open('tunnelURL.txt') as file:
    tunnelURL = file.read()
os.remove('tunnelURL.txt')

print(f"Tunnel created at URL: {tunnelURL}")

# posting endpoint to GaussDB server
data = {
    "userId": userId,
    "tunnelUrl": tunnelURL
}

response = requests.post(endpointUpdateURL, json=data)

if response.status_code != 200:
    print(f"\nENDPOINT POST ERROR: {response.status_code} | {response.text}")
else:
    print(f"tunnelURl {tunnelURL} has been updated to database")

# flask server
app = flask.Flask(__name__)

@app.route('/announceMessage', methods=['POST'])
def announceMessage():
    try:
        # get json value from request
        content = flask.request.json
        text = content['text']
        print(f"Received message: {text}")
        
    except Exception as e:
        print(e)
        return 'Invalid JSON'

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
    return "OK"

@app.route('/announceAudio', methods=['POST'])
def announceAudio():
    try:
        content = flask.request.json
        URL = content['URL']

    except Exception as e:
        print(e)
        return 'Invalid JSON'

    # play audio
    # this is still in progress

    return 'OK'

@app.route('/')
def index():
    return f"Server is running on {tunnelURL}"

app.run(host='localhost', port=5000)
