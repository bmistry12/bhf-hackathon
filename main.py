import re
import csv
import json
import xlwt
import math
import pprint
import requests
from math import radians, cos, sin, asin, sqrt


class Main():
    def __init__(self):
        self.allRows = []
        self.csvname = 'test.csv'
        process(self)
        batch(self)
        # leave out for now
        # updateCSV(self)


def process(self):
    i = 0
    f = open(self.csvname)
    csv_f = csv.reader(f)
    long_col = []
    lat_col = []
    for row in csv_f:
        if (i > 0):
            postcode = sanitizePostcodes(str(row))
            response = requests.get(
                'http://api.postcodes.io/postcodes/' + postcode)
            parsed_json = json.loads(response.content)
            print(parsed_json)
            longitude = parsed_json.get('result').get('longitude')
            long_col.append(str(longitude))
            latitude = (parsed_json.get('result').get('latitude'))
            lat_col.append(str(latitude))
        i = i + 1
    f.close()
    configureRows(self, long_col, lat_col)


def sanitizePostcodes(line):
    for char in line:
        if char.isspace():
            line = line
        elif not char.isalnum():
            line = line.replace(char, "")
    return(line)


def configureRows(self, long_col, lat_col):
    f = open(self.csvname)
    csv_f = csv.reader(f)
    count = 0
    for row in csv_f:
        if(count == 0):
            row.append('Longitude')
            row.append('Latitude')
            print(row)
        else:
            row.append(long_col[count-1])
            row.append(lat_col[count-1])
            print(row)
        self.allRows.append(row)
        count = count + 1
    f.close()


def updateCSV(self):
    print("Write New Rows")
    outputFile = open(self.csvname, 'w')
    newRows = pprint.pformat(self.allRows)
    newRows = re.sub("\[|\]|\'", "", newRows)
    outputFile.write(newRows)
    outputFile.close()
    print("Done")

# This is a disgusting way of doing this but enumerate is being a pain
def batch(self):
    distances = []
    # get distances between all the points - I can imagine this being very inefficient with tonnes of data but meh
    for i in range(len(self.allRows)):
        if i > 0:
            row = self.allRows[i]
            print(i)
            for j in range(len(self.allRows)):
                if j > i :
                    row2 = self.allRows[j]
                    print(j)
                    dist = calcDist(float(row[1]), float(row[2]), float(row2[1]), float(row2[2]))
                    print(str(dist))
                    distances.append((row[0], row2[0], str(dist)))
    # List of tupes with two postcodes and the distance between them in km
    # We need some sort of bound to decide what determines there nearby...
    print(distances)


def calcDist(lat1, lon1, lat2, lon2):
    # Uses Haversine formula
    radius = 6371 # km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d
