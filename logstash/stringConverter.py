import csv
import numpy as np
import math
import os
import time

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

with open('csv/logs.csv', 'r', encoding='UTF8', newline='') as myfile, open('csv/logs2D.csv', 'a', encoding='UTF8', newline='') as mynewfile:
    reader = csv.reader(myfile, escapechar=' ')
    wr = csv.writer(mynewfile, quoting=csv.QUOTE_NONE, escapechar=' ')

    counter = 0
    while counter < 5000:         #if i wait for 50 iteration, stop the application
        for row in reader:
                if len(row) > 23:
                    n_row = []
                    n_row = coord_converter(row[1:])
                    #n_row = n_row[:-1]
                    n_row.insert(0, row[0])
                    #print(n_row)
                    wr.writerow(n_row)
                    counter -= 1
                else:
                    counter += 1
    print("no data coming")