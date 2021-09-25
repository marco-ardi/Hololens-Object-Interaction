import numpy as np
import cv2 as cv
import os
import time
from datetime import datetime

def getLDAP():
    ldap = (((datetime.now() - datetime(1970,1,1)).total_seconds())+11644473600)*10000000
    ldap = f"{ldap:.18f}"
    ldap = str(ldap)
    ldap = ldap.split(".")[0]
    print("ldap =", ldap)
    return ldap
    




user = "ADMIN"
pw = "ADMIN172839"
addr = "192.168.60.34"    #controlla che sia giusto, all'ip di hololens piace cambiare
cap = cv.VideoCapture("https://"+ user +":"+ pw +"@"+addr+"/api/holographic/stream/live_high.mp4?holo=true&pv=true&mic=true&loopback=true")
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    img = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)     #cv.COLOR_BGR2GRAY

    
    ldap = getLDAP()

    path = 'C:/Users/marco/Desktop/Tesi/timestampPhotos'
    cv.imwrite(os.path.join(path , ldap+".png"), img)
    # Display the resulting frame
    cv.imshow('frame', img)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()