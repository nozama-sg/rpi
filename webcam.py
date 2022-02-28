
import os, time, cv2

sleepTime = 5

while True:
    fileList = os.listdir('images')
    fullPath = [f"images/{name}" for name in fileList]

    if len([name for name in fileList]) > 10:
        oldestFile = min(fullPath, key=os.path.getctime)
        os.remove(oldestFile)

    fileList = os.listdir('images')
    fullPath = [f"images/{name}" for name in fileList]

    if len([name for name in fileList]) == 0:
        count = 1
    else:
        newestFile = max(fullPath, key=os.path.getctime)
        count = int(newestFile.split('/')[-1].split('.')[0].split('_')[-1]) + 1

    cam = cv2.VideoCapture(0)
    s, img = cam.read()

    cam.release()
    time.sleep(sleepTime)

    if s: 
        print(cv2.imwrite(f"/home/pi/Documents/huawei-hackathon/rpi/images/image_{count}.jpg",img)) #save image

    src_prevImage = cv2.imread("/home/pi/Documents/huawei-hackathon/rpi/images/image_{count -1}.jpg")
    src_currentImage = cv2.imread("/home/pi/Documents/huawei-hackathon/rpi/images/image_{count}.jpg")

    hsv_prevImage = cv2.cvtColor(src_prevImage, cv2.COLOR_BGR2HSV)
    hsv_currentImage = cv2.cvtColor(src_currentImage, cv2.COLOR_BGR2HSV)

    # calculate the absolute difference between the current and previous image
    frameDelta = cv2.absdiff(hsv_prevImage, hsv_currentImage)

    # return numeric value of differnce between images
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    print(thresh)