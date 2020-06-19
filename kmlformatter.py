#!/bin/python3

def placemarkSkeleton(id, lon, lat, networks, time):
    data = f"""
  <Placemark>
    <name>{id}</name>
    <description>{networks}</description> 
    <Point>
      <coordinates>{lon},{lat},0</coordinates>
    </Point>
  </Placemark>"""
    return data

def main():
    file = open("data.kml","w")
    with open("data.sql") as f:
        data = f.readlines()
    start = """
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>"""
    file.write(start.lstrip())
    for line in data:
        id, lon, lat, networks, time = line.rstrip().split('|')
        file.write(placemarkSkeleton(id, lon, lat, networks, time))
    end = """  
  </Document>
</kml>"""
    file.write(end)
    file.close()

if __name__ == '__main__':
    main()

