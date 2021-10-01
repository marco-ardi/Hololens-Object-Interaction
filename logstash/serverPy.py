import socket
import cv2
import io
import csv
import numpy as np


HOST = '192.168.1.10' # Host address
PORT = 9999        # Port to listen on (non-privileged ports are > 1023)

def recv_by_step(conn, size):
    immagine = bytearray()
    mul = size // 8192
    reminder = size % 8192
    for i in range(mul):
        immagine+=conn.recv(8192)
    immagine+= conn.recv(reminder)
    return immagine


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
                try:
                    str_size = conn.recv(8).decode('utf-8') #TODO In C# usare str(len(string)).padRight(8,"0").encode()
                    print("str_size = " + str_size)

                    stringdata = conn.recv(int(str_size)).decode("utf-8")
                    print("String: ", stringdata)
                except Exception:
                   break
                if not stringdata: continue  

                received_data = stringdata.split(' ')
                wr.writerow(received_data)

                dim = conn.recv(8)
                print("dim=")
                print(dim)
                dim = dim.decode("utf-8")
                print("dim = "+dim)
                img = recv_by_step(conn, int(dim))
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