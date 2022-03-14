import flask
import time
import os
import requests
import pyttsx3
import vlc
import userpass
import sqlite3
from pyngrok import ngrok
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

userId = 22
endpointUpdateURL = 'http://119.13.104.214:80/announcementEndpointUpdate'
ngrok.set_auth_token(userpass.token)

# creating tunnel endpoint
print("Creating Tunnel")
ngrok_tunnel = ngrok.connect(5000)
tunnelURL = ngrok_tunnel.public_url
print(f"Tunnel created at URL: {tunnelURL}")

# posting endpoint to GaussDB server
data = {
    "userId": userId,
    "tunnelUrl": tunnelURL
}

try:
    response = requests.post(endpointUpdateURL, json=data)

    if response.status_code != 200:
        print(f"\nENDPOINT POST ERROR: {response.status_code} | {response.text}")
    else:
        print(f"tunnelURl {tunnelURL} has been updated to database")

except:
    print('ERROR: Unable to update server endpoint')

def announceReminder():
    print(reminderTimeUUID)
    db = sqlite3.connect('reminders.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    medicineName = cursor.execute("SELECT medicine FROM medicine INNERJOIN reminderTime on medicine.medicineReminderId = reminderTime.medicineReminderId WHERE reminderTime.reminderTimeUUID = ?", (reminderTimeUUID,)).fetchone()

    print(medicineName)

    engine = pyttsx3.init()
    engine.say(f"This is a reminder to take your {medicineName['medicine']} medicine.")
    engine.runAndWait()
    time.sleep(1)
    engine.say(f"This is a reminder to take your {medicineName['medicine']} medicine.")
    engine.runAndWait()

# flask server
app = flask.Flask(__name__)

# announceAudio + sendAudio

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

    # get the list of files in the directory and fullPath of files
    fileList = os.listdir('announceMessage')
    fullPath = [f"./announceMessage/{name}" for name in fileList]
    
    # determining fileName
    if len([name for name in fileList]) == 0:
            count = 1
    else:
        newestFile = max(fullPath, key=os.path.getctime)
        count = int(newestFile.split('/')[-1].split('.')[0].split('_')[-1]) + 1

    # save message to file
    with open(f"./announceMessage/message_{count}.txt", "w") as file:
        file.writelines(text)

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

    except Exception as e:
        print(f"Error: {e}")
        print(content)
        return 'Invalid JSON for announceAudio'

    fileType = URL.split('.')[-1]

    # get the list of files in the directory and fullPath of files
    fileList = os.listdir('announceAudio')
    fullPath = [f"./announceAudio/{name}" for name in fileList]

    # remove oldest file
    if len([name for name in fileList]) > 10:
        oldestFile = min(fullPath, key=os.path.getctime)
        os.remove(oldestFile)

    # update list of files in dir and fullpath of files
    fileList = os.listdir('announceAudio')
    fullPath = [f"./announceAudio/{name}" for name in fileList]

    # determining new file name
    if len([name for name in fileList]) == 0:
        count = 1
    else:
        newestFile = max(fullPath, key=os.path.getctime)
        count = int(newestFile.split('/')[-1].split('.')[0].split('_')[-1]) + 1

    # download audio file
    r = requests.get(URL)
    with open(f"./announceAudio/audio_{count}.{fileType}", "wb") as f:
        f.write(r.content)
    
    # play audio file
    player = vlc.MediaPlayer(f"./announceAudio/audio_{count}.{fileType}")
    player.play()

    return 'OK'

@app.route('/medicineReminder/new', methods=['POST'])
def addMedicineReminder():
    db = sqlite3.connect('reminders.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    try:
        userId = flask.request.json['userId']
        medicine = flask.request.json['medicine']
        timeList = flask.request.json['time']
    except Exception as e:
        return f"Invalid JSON, Error: {e}"

    result = cursor.execute("SELECT * FROM medicine WHERE userId = {userId} AND medicine = '{medicine}'").fetchall()
    if len(result) != 0:
        return f"Already exists"

    # get generated medicine ID
    cursor.execute(f"INSERT INTO medicine(userId, medicine) VALUES (?,?)",(userId, medicine))
    db.commit()

    medicineReminderId = cursor.execute("SELECT * FROM medicine WHERE userId = {userId} AND medicine = '{medicine}'").fetchall()[0]['medicineReminderId']

    # insert timing into reminderTime
    for time in timeList:
        cursor.execute(f"INSERT INTO reminderTime(medicineReminderId, reminderTIme) VALUES ({medicineReminderId}, {time})")

        reminderTimeUUID = cursor.execute(f"SELECT * FROM reminderTime WHERE medicineReminderId = {medicineReminderId} AND reminderTime = {time}").fetchall()[0]['reminderTimeUUID']

        hourNum = int(time.split(':')[0])
        minuteNum = int(time.split(':')[1])

        scheduler.add_job(announceReminder, 'cron', hour=hourNum, minutes=minNum, id=reminderTimeUUID, args=[reminderTimeUUID])

    db.commit()

    return medicineReminderId

@app.route('/medicineReminder/delete', methods=['POST'])
def deleteMedicineReminder():
    db = sqlite3.connect('reminders.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    try:
        medicineReminderId = flask.request.json['medicineReminderId']
    except Exception as e:
        return f"Invalid JSON, Error: {e}"

    result = cursor.execute(f"SELECT * FROM medicine WHERE medicineReminderId = {medicineReminderId}").fetchall()

    if len(result) == 0:
        return f"Medicine does not exist"

    reminders = cursor.execute(f"SELECT * FROM reminderTime WHERE medicineReminderId = {medicineReminderId}").fetchall()

    for reminder in reminders:
        scheduler.remove_job(reminder['reminderTimeUUID'])

    return 'OK'

@app.route('/')
def index():
    return f"Server is running on {tunnelURL}"

app.run(host='0.0.0.0', port=5000)
