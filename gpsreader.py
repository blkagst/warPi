#! /usr/bin/python

import signal 
from gps import *
from time import *
import time
import threading
import datetime
import sqlite3, subprocess, re, os

gpsd = None 

def parseData(in_data):
    string = ''.join(in_data)
    lst    = re.split(r'Cell \d\d..', string)[1:]
    dict = [] 
    for data in lst:
        try:
            address = re.search('ESSID:"([^"]*)"', data).group(1)
        except:
            address = 'N/A'
        try:
            encryption_key = re.search(r'Encryption key:([^\n]*)\n', data).group(1)
        except:
            encryption_key = 'N/A'
        try:
            encryption = re.search(r'IE: (IEEE[^\n]*)\n', data).group(1)
        except:
            encryption = 'N/A'
        dict.append('{} EncryptionKey:{} Encryption:{}'.format(address,encryption_key,encryption))
    return ', '.join(dict)

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
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd 
    gpsd = gps(mode=WATCH_ENABLE) 
    self.current_value = None
    self.running = True 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() 

if __name__ == '__main__':
  if os.geteuid() == 0:
      os.system("stty -F /dev/ttyAMA0 9600")
      os.system("gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
      os.system("ifconfig wlan0 down")
      os.system("ifconfig wlan0 up")
  gpsp = GpsPoller() 
  try:
    gpsp.start() 
    day = 'a' + str(datetime.datetime.now().date()).replace('-','')
    conn = createTable(day)
    while True:
      lat = gpsd.fix.latitude
      lon = gpsd.fix.longitude
      data = (lon, lat)
      if lat == 0.0 or lon == 0.0:
          time.sleep(5)
          continue
      logData(day, conn, data)
      time.sleep(2) 
  except (KeyboardInterrupt, SystemExit): 
    conn.close()
    gpsp.running = False
    gpsp.join() 
