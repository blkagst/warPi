#! /usr/bin/python

import datetime
import os
import re
import sqlite3
import threading
import time
from time import *

from gps import *

gpsd = None

def parseData(in_data):
    string = ''.join(in_data)
    lst = re.split(r'Cell \d\d..', string)[1:]
    network_data = []

    for _data in lst:
        try:
            address = re.search('ESSID:"([^"]*)"', _data).group(1)
        except:
            address = 'N/A'
        try:
            encryption_key = re.search(r'Encryption key:([^\n]*)\n', _data).group(1)
        except:
            encryption_key = 'N/A'
        try:
            encryption = re.search(r'IE: (IEEE[^\n]*)\n', _data).group(1)
        except:
            encryption = 'N/A'
        network_data.append('{} EncryptionKey:{} Encryption:{}'.format(address, \
                encryption_key, encryption))

    return ', '.join(network_data)

def createTable(name):
    conn = sqlite3.connect('/home/pi/Documents/sensordata.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS \
            {}(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                    LON     TEXT    NOT NULL, \
                    LAT     TEXT    NOT NULL,   \
                    NETWORKS TEXT, \
                    TIME    TEXT            NOT NULL);'''.format(name))

    return conn

def logData(table, conn, data):
    lon, lat = data[0], data[1]

    if lon == 'nan':
        return True
    data = parseData(os.popen('iwlist wlan0 scan').read())
    conn.execute('''INSERT INTO {} (LON, LAT, NETWORKS, TIME) \
            VALUES ({}, {}, '{}', time('now'));'''.format(table, lon, lat, data))
    conn.commit()

    return True

class GpsPoller(threading.Thread):
    """Gps Poller"""
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd
        gpsd = gps(mode=WATCH_ENABLE)
        self.current_value = None
        self.running = True

if __name__ == '__main__':
    if os.geteuid() == 0:
        """If running as root, init psudo term connection and start gpsd"""
        os.system("stty -F /dev/ttyAMA0 9600")
        os.system("gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
        os.system("ifconfig wlan0 down")
        os.system("ifconfig wlan0 up")
        gpsp = GpsPoller()
    try:
        gpsp.start()
        day = 'a' + str(datetime.datetime.now().date()).replace('-', '')
        connection = createTable(day)

        while True:
            lat = gpsd.fix.latitude
            lon = gpsd.fix.longitude
            data = (lon, lat)
            if lat == 0.0 or lon == 0.0:
                logData(day, connection, data)
                time.sleep(10)

                continue
            logData(day, connection, data)
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        connection.close()
        gpsp.running = False
        gpsp.join()
