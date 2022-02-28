
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

    # compute the correlation between the two images
    # compute the value of the correlation
    # if the value is greater than 0.9, then it is a match
    # if the value is less than 0.9, then it is not a match
    (score, diff) = cv2.compareHist(hist_prevImage, hist_currentImage, cv2.HISTCMP_CORREL)
    print(score)
    if score > 0.9:
        print("Match")
    else:
        print("No Match")