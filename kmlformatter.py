#!/bin/python3

import datetime
import sqlite3


def placemarkSkeleton(_id, lon, lat, networks, time):
    data = f"""
  <Placemark>
    <name>{id}</name>
    <description>{networks}</description>
    <Point>
      <coordinates>{lon},{lat},0</coordinates>
    </Point>
  </Placemark>"""
    return data

def writeToFile(file, data):
    start = """
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>"""
    file.write(start.lstrip())

    for line in data:
        _id, lon, lat, networks, time = line.rstrip().split('|')
        file.write(placemarkSkeleton(_id, lon, lat, networks, time))
    end = """
  </Document>
</kml>"""
    file.write(end)
    file.close()

def main():
    file = open("/home/pi/Documents/data.kml", "w")
    conn = sqlite3.connect('/home/pi/Documents/sensordata.db')
    conn.execute('.output /home/pi/Documents/data.kml')
    day = 'a' + str(datetime.datetime.now().date()).replace('-', '')
    conn.execute('select * from {};'.format(day))
    conn.close()
    with open("/home/pi/Documents/data.sql") as f:
        data = f.readlines()
    writeToFile(file, data)

if __name__ == '__main__':
    main()
