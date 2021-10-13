import socket
import cv2
import io
import csv
import json
import base64
import numpy as np
from ftfy import fix_text
import json



HOST = '172.20.10.5' # Host address
PORT = 9999        # Port to listen on (non-privileged ports are > 1023)

def recv_by_step(conn, size):
    immagine = bytearray()
    mul = size // 8192
    reminder = size % 8192
    for i in range(mul):
        immagine+=conn.recv(8192, socket.MSG_WAITALL)
    immagine+= conn.recv(reminder, socket.MSG_WAITALL)
    print("i received:" + str(immagine))
    return immagine


def recv_json(conn, size):
    #json_data = recv_by_step(conn, size).decode("utf-8")
    json_data = conn.recv(size, socket.MSG_WAITALL).decode("utf-8")
    # text = some text source with a potential unicode problem
    fixed_text = fix_text(json_data)
    print(fixed_text)
    parsed_data = json.loads(fixed_text)
    #parsed_data = json.loads(json_data)
    return parsed_data["msg"], base64.b64decode(parsed_data["img"])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("listening on:" + HOST +":"+ str(PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256000)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()

    with open('csv/logs.csv', 'a', encoding='utf-8', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_NONE, escapechar=' ')
        with conn:
            print('Connected by', addr)
            while True:
                json_size = conn.recv(8).decode('utf-8')
                print("json_size=" + json_size)

                stringdata, img =recv_json(conn, int(json_size))
                #try:
                    #str_size = conn.recv(8).decode('utf-8') #TODO In C# usare str(len(string)).padRight(8,"0").encode()
                    #print("str_size = " + str_size)

                    #stringdata = conn.recv(int(str_size)).decode("utf-8")
                    #print("String: ", stringdata)
                #except Exception as e:
                    #print(e)
                    #break
                #if not stringdata: continue  

                received_data = stringdata.split(' ')
                wr.writerow(received_data)

                #dim = conn.recv(8)
                #print("dim=")
                #print(dim)
                #dim = dim.decode("utf-8")
                #print("dim = "+dim)
                #img = recv_by_step(conn, int(dim))
                #img = conn.recv(int(dim))
                print(img[:-10])
                # img = conn.recv(int(dim)) #worst case scenario for a 1280x720 jpeg image is 160000 bytes
                #print(img)

                if not img: continue         #it is 2764800 bytes for a 1280x720 png image
                try:
                    file_bytes = np.asarray(bytearray(io.BytesIO(img).read()), dtype=np.uint8)    
                    imgToShow = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    cv2.imwrite("csv/" + received_data[0] +'.jpg', imgToShow)
                except Exception as e:
                    print("errore:", e)
                    True