import numpy as np
import cv2 as cv
import os
import time
from datetime import datetime

def getLDAP():
    #ldap = (((datetime.now() - datetime(1970,1,1)).total_seconds())+11644473600)
    #ldap = f"{ldap:.18f}"   #i think it must be .11f           #now it should give back unix timestamp at microseconds precision
    ldap = ((datetime.now() - datetime(1970,1,1)).total_microseconds()) #if it works, rename ldap to timestamp
    ldap = str(ldap)
    ldap = ldap[:-3]    #should cut the last 3 chars (microseconds, we only want milliseconds)
    ldap = ldap.split(".")[0]
    print("ldap =", ldap)
    return ldap
    
def connect():
    user = "ADMIN"
    pw = "ADMIN172839"
    addr = "192.168.60.34"    #controlla che sia giusto, all'ip di hololens piace cambiare
    cap = cv.VideoCapture("https://"+ user +":"+ pw +"@"+addr+"/api/holographic/stream/live_high.mp4?holo=false&pv=true&mic=false&loopback=true")
    cap.set(cv.CV_CAP_PROP_FPS, 30) #should limit fps to 30 
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    return cap

def getFrames(cap, path = 'C:/Users/marco/Desktop/Tesi/timestampPhotos'):
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # Our operations on the frame come here
        img = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)     #cv.COLOR_BGR2GRAY
        #getting LDAP.png name
        ldap = getLDAP()
        #save images in path        
        cv.imwrite(os.path.join(path , ldap+".png"), img)
        # Display the resulting frame
        cv.imshow('frame', img)
        if cv.waitKey(1) == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

def fixTimestamp(img_ts, data_ts):                          #every timestamp is fixed to milliseconds precision
    if(img_ts + 35 >= data_ts or img_ts -35 <= data_ts):    #we (might) take 30 frames per second, so it is important to fix frame and data timestamps
        return True             #same moment                #let's divide a second (which is equal to 1000ms) per 30 frames : 
    else:                                                   #1000/30 = 33.3 -> if a timestamp is 35ms more or less than another, we assume it belongs to the same frame
        return False            #different moment

if __name__ == "__main__":
    cap = connect()
    getFrames(cap)