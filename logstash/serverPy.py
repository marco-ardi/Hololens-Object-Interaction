import socket
import cv2
import io
import os
import time
import math
import csv
import json
import base64
import numpy as np
from ftfy import fix_text
import json


HOST = '172.20.10.5' # Host address
PORT = 9999        # Port to listen on (non-privileged ports are > 1023)
focal_l = 1300
center_x = 1280/2
center_y = 720/2

def coord_converter(str):
    j=0
    converted_str = []
    for i in range(0,11):                  #3 coordinate per occhi + 3*5*2 coordinate per  dita
        point=[float(str[i+j]), float(str[i+j+1]), float(str[i+j+2])]
        if(point[0]==-1 or point[1]==-1 or point[2]==-1):
            j+=2
            converted_str.append(-1)
            converted_str.append(-1)
            continue                       #se un punto è uguale a -1, allora lo skippo

        x = focal_l * ((1.52048 * point[0]) / point[2]) 
        y = focal_l * ((1.52048 * point[1]) / point[2])
        x += 1280 / 2
        y = (720 / 2) - y

        x2 = (int)(x-np.sign(x-center_x)*math.sqrt(abs(x-center_x)*16))
        y2 = (int)(y-np.sign(y-center_y)*math.sqrt(abs(y-center_y)*9))
        converted_str.append(x2)
        converted_str.append(y2)
        j+=2
    return converted_str

def recv_json(conn, size):
    json_data = conn.recv(size, socket.MSG_WAITALL).decode("utf-8")
    fixed_text = fix_text(json_data)
    #print(fixed_text)
    parsed_data = json.loads(fixed_text)
    return parsed_data["msg"], base64.b64decode(parsed_data["img"])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("listening on:" + HOST +":"+ str(PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256000)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()

    with open('csv/logs2D.csv', 'a', encoding='utf-8', newline='') as mynewfile:
        wr2D = csv.writer(mynewfile, quoting=csv.QUOTE_NONE, escapechar=' ')

        with conn:
            print('Connected by', addr)
            while True:
                json_size = conn.recv(8).decode('utf-8')
                print("json_size=" + json_size)

                stringdata, img =recv_json(conn, int(json_size))

                received_data = stringdata.split(' ')
                #wr.writerow(received_data)
                row = received_data
                new_row =[]
                new_row = coord_converter(row[1:])
                new_row.insert(0, row[0])
                print(new_row)
                wr2D.writerow(new_row)
                mynewfile.flush()
                if not img: continue         #it is 2764800 bytes for a 1280x720 png image
                try:
                    file_bytes = np.asarray(bytearray(io.BytesIO(img).read()), dtype=np.uint8)    
                    imgToShow = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    cv2.imwrite("csv/input_imgs/" + received_data[0] +'.jpg', imgToShow)
                except Exception as e:
                    print("errore:", e)
                    True