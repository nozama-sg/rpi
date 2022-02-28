
import os, time, cv2

sleepTime = 5

while True:
    fileList = os.listdir('images')
    fullPath = [f"images/{name}" for name in fileList]

    if len([name for name in fileList]) == 10:
        oldestFile = min(fullPath, key=os.path.getctime)
        os.remove(oldest_file)

    if len([name for name in fileList]) == 0:
        count = 0
    else:
        newestFile = max(fullPath, key=os.path.getctime)
        count = int(newestFile.split('/')[-1].split('.')[0])

    cam = cv2.VideoCapture(0) 
    s, img = cam.read()

    time.sleep(sleepTime)

    if s:    # frame captured without any errors
        # namedWindow("cam-test",WINDOW_AUTOSIZE)
        # imshow("cam-test",img)
        # waitKey(0)
        # destroyWindow("cam-test")
        
        cv2.imwrite(f"images/image_{count}",img) #save image
        count += 1