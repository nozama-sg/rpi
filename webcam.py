import os, cv2, requests, base64, json

shortSleep = 60 * 5
longSleep = 60 * 20

# testing
shortSleep = 5
longSleep = 20

sleepTime = shortSleep
matchValue = 0.7
positiveResponse = 0
userId = "darentan"

def checkImage(count):
    src_prevImage = cv2.imread(f"/home/pi/Documents/huawei-hackathon/rpi/images/image_{count-1}.jpg")
    src_currentImage = cv2.imread(f"/home/pi/Documents/huawei-hackathon/rpi/images/image_{count}.jpg")

    # opencv compare histogram between src_prevImage and src_currentImage
    # if the difference is less than 10%, then it is a match

    # convert the images to grayscale
    gray_prevImage = cv2.cvtColor(src_prevImage, cv2.COLOR_BGR2GRAY)
    gray_currentImage = cv2.cvtColor(src_currentImage, cv2.COLOR_BGR2GRAY)

    # compute the histogram of the two images and normalize
    hist_prevImage = cv2.calcHist([gray_prevImage], [0], None, [256], [0, 256])
    hist_currentImage = cv2.calcHist([gray_currentImage], [0], None, [256], [0, 256])
    hist_prevImage = cv2.normalize(hist_prevImage, hist_prevImage, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    hist_currentImage = cv2.normalize(hist_currentImage, hist_currentImage, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)

    # compute the value of the correlation
    score = cv2.compareHist(hist_prevImage, hist_currentImage, cv2.HISTCMP_CORREL)

    return score

def postImageRekognition(imageName):
    with open(f"images/{imageName}.jpg", "rb") as imageFile:
        imageData = base64.b64encode(imageFile.read())
    
    data = {
        "b64": imageData.decode()
    }
    
    response = requests.post("http://localhost:4000/api/Upload", json=data)
    
    # read response in json
    response = json.loads(response.text)

    return response

def postImageHuawei(imageName, userId):
    with open(f"images/{imageName}.jpg", "rb") as imageFile:
        imageData = base64.b64encode(imageFile.read())

    data = {
        "userId": userId
    }

    response = requests.post("http://119.13.104.214:80/uploadFoodImage", json=data)

    return response

while True:
    # get the list of files in the directory and fullPath of files
    fileList = os.listdir('images')
    fullPath = [f"images/{name}" for name in fileList]

    # remove oldest file
    if len([name for name in fileList]) > 10:
        oldestFile = min(fullPath, key=os.path.getctime)
        os.remove(oldestFile)

    # update list of files in dir and fullpath of files
    fileList = os.listdir('images')
    fullPath = [f"images/{name}" for name in fileList]

    # determining new file name
    if len([name for name in fileList]) == 0:
        count = 1
    else:
        newestFile = max(fullPath, key=os.path.getctime)
        count = int(newestFile.split('/')[-1].split('.')[0].split('_')[-1]) + 1

    # capture image with cv2
    cam = cv2.VideoCapture(0)
    s, img = cam.read()
    cam.release()

    # save image
    if s:
        print(cv2.imwrite(f"/home/pi/Documents/huawei-hackathon/rpi/images/image_{count}.jpg",img)) 

    # comparison with previous image
    if count > 1:
        score = checkImage(count)

        if score >= matchValue: # if match
            print(f"Match between image_{count-1}.jpg and image_{count} with score {score}")
        else: # no match
            print(f"No Match between image_{count-1}.jpg and image_{count}. Score: {score}")

            
            # testing
                        
            # send data to AWS
            # rekognitionResponse = postImageRekognition(count)
            # categories = [name['Name'] for name in rekognitionResponse]

            categories = ['Dish']

            if "Dish" in categories or "Meal" in categories or "Food" in categories:
                positiveResponse += 1
                sleepTime = longSleep

                if positiveResponse == 1:
                    # send to OBS
                    postImageHuawei(count, userId)
                    print(f"Image {count}.jpg has been uploaded to Huawei OBS")

                else:
                    print(f"{positiveResponses} logs of food have occured previously. Data is not being sent.")

            else:
                print("No food detected")
                positiveResponse = 0
                sleepTime = shortSleep
        
    time.sleep(sleepTime)