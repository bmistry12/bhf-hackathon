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
        self.riskFactor = []
        # Name of the csv to process
        self.csvname = 'test-small.csv'
        process(self)
        batch(self)
        # leave out for now
        # updateCSV(self)

# Go through the CSV and identify latitude and longitute for each postcode
def process(self):
    i = 0
    f = open(self.csvname)
    csv_f = csv.reader(f)
    long_col = []
    lat_col = []
    for row in csv_f:
        if (i > 0):
            postcode = sanitizePostcodes(str(row))
            # Initialise risk array (with value of 0) for this postocde
            self.riskFactor.append((postcode, 0))
            #Call the Postcodes.io api - this returns a json with all kinds of info about the postcode
            response = requests.get("http://api.postcodes.io/postcodes/' + postcode)
            parsed_json = json.loads(response.content)
            print(parsed_json) # for debugging
            longitude = parsed_json.get('result').get('longitude')
            long_col.append(str(longitude))
            latitude = (parsed_json.get('result').get('latitude'))
            lat_col.append(str(latitude))
        i = i + 1
    f.close()
    # Create the lang and lat rows for the csv file
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
    # for each row add its contents into an array and then add any additional data as required
    for row in csv_f:
        #first row == headings
        if(count == 0):
            row.append('Longitude')
            row.append('Latitude')
            print(row)
        # data rows 
        else:
            row.append(long_col[count-1])
            row.append(lat_col[count-1])
            print(row)
        self.allRows.append(row)
        count = count + 1
    f.close()

# Update the CSV to contain all the new data! (Final Step)
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
                    distances.append([row[0], row2[0], str(dist)])
   # List of arrays with two postcodes and the distance between them 
    print(distances)
    # Start evaluating the risk of a postcode needing to be batched 
    evaluateRisk(self, distances)


def calcDist(lat1, lon1, lat2, lon2):
    # Uses Haversine formula to determine the greatest circular distance between two points in miles
    radius = 3958.756  # miles # use 6371 for km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

# Determine the probability of needing to batch each postcodes order 
def evaluateRisk(self, distances):
    threshold = 0.5 #miles
    for group in distances:
        if (float(group[2]) <= threshold):
            print(group[0])
            print(group[1])
            increaseRisk(group[0], self)
            increaseRisk(group[1], self)
            print("These are nearby - potentially batch them!")
    # The greater the risk the higher the chance of required batching
    print("Final risks")
    print (self.riskFactor)

#Increment risk for the particular postcode
# Currently re-orders postcodes which may be cause adding new data to be slighly more inefficient and complex but we shall see
def increaseRisk(postcode, self):
    toRemove = []
    toReAdd = []
    for (code, risk) in self.riskFactor:
        if code == postcode :
            newRisk = risk + 1
            toReAdd.append((code, newRisk))
            toRemove.append((code, risk))
    for item in toRemove:
        self.riskFactor.remove(item)
    for item in toReAdd:
        self.riskFactor.append(item)
