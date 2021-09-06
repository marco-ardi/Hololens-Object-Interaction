import socket
import cv2
import io
import csv
import numpy as np

HOST = '172.26.106.119' # Host address
PORT = 9999        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("listening on:" + HOST +":"+ str(PORT))
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with open('csv/logs.csv', 'a', encoding='utf-8', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_NONE, escapechar=' ')
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024*8)
                stringdata = data.decode('utf-8')

                print("String: ", stringdata)
                if not data: continue  

                received_data = []
                received_data = stringdata.split(' ')



                wr.writerow(received_data)

                img = conn.recv(160000) #worst case scenario for a 1280x720 jpeg image is 160000 bytes
                if not img: continue         #it is 2764800 bytes for a 1280x720 png image
                try:
                    print("Ho ricevuto l'immagine")
                    file_bytes = np.asarray(bytearray(io.BytesIO(img).read()), dtype=np.uint8)
                    #file_bytes = np.frombuffer (img, np.uint8)
                    imgToShow = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    #print(imgToShow.shape)
                    cv2.imwrite('csv/'+ received_data[0] +'.jpg', imgToShow)
                    #plt.imshow(imgToShow)
                    #plt.show() 
                    #if not data:
                    #    break
                except Exception as e:
                    print("errore:", e)
                    True