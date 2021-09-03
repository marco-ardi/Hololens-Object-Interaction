import csv
import random

with open('/home/marco/progetto/logstash/csv/logs2D.csv', 'a', encoding='UTF8', newline='') as mynewfile:
    wr = csv.writer(mynewfile, quoting=csv.QUOTE_NONE, escapechar=' ')
    for i in range(0,100):
        row = str(random.randint(0,10000)) + str(random.randint(0,10000)) + str(random.randint(0,10000)) + str(random.randint(0,10000)) + str(random.randint(0,10000)) + str(random.randint(0,10000)) +str(random.randint(0,10000))
        wr.writerow(row)