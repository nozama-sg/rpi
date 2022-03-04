import flask
import subprocess
import time
import os
import requests
import pyttsx3
import vlc

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

# TODO
# announceAudio, recordAudio + sendAudio

@app.route('/announceMessage', methods=['POST'])
def announceMessage():
    try:
        # get json value from request
        content = flask.request.json
        text = content['text']
        print(f"Received message: {text}")
        
    except Exception as e:
        print(e)
        return 'Invalid JSON for announceMessage'

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
    return "OK"

@app.route('/announceAudio', methods=['POST'])
def announceAudio():
    try:
        content = flask.request.json
        URL = content['URL']
        print(f"Received audio: {URL}")

        fileType = URL.split('.')[-1]

        # get the list of files in the directory and fullPath of files
        fileList = os.listdir('announceAudio')
        fullPath = [f"announceAudio/{name}" for name in fileList]

        # remove oldest file
        if len([name for name in fileList]) > 10:
            oldestFile = min(fullPath, key=os.path.getctime)
            os.remove(oldestFile)

        # update list of files in dir and fullpath of files
        fileList = os.listdir('announceAudio')
        fullPath = [f"announceAudio/{name}" for name in fileList]

        # determining new file name
        if len([name for name in fileList]) == 0:
            count = 1
        else:
            newestFile = max(fullPath, key=os.path.getctime)
            count = int(newestFile.split('/')[-1].split('.')[0].split('_')[-1]) + 1

        # download audio file
        r = requests.get(URL)
        with open(f"announceAudio/audio_{count}.{fileType}", "wb") as f:
            f.write(r.content)
        
        # play audio file
        player = vlc.MediaPlayer(f"/announceAudio/audio_{count}.{fileType}")
        player.play()

    except Exception as e:
        print(e)
        return 'Invalid JSON for announceAudio'

    return 'OK'

@app.route('/')
def index():
    return f"Server is running on {tunnelURL}"

app.run(host='localhost', port=5000)
