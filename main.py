import re
import csv
import json
import xlwt
import pprint
import requests

class Main():
    def __init__(self):
        self.csvname = 'test.csv'
        process(self)


def process(self):
    i = 0
    f = open(self.csvname)
    csv_f = csv.reader(f)
    long_col = []
    lat_col = []
    for row in csv_f:
        if (i > 0):
            postcode = sanitizePostcodes(str(row))
            response = requests.get('http://api.postcodes.io/postcodes/' + postcode)
            parsed_json = json.loads(response.content)
            longitude = parsed_json.get('newRows').get('longitude')
            long_col.append(str(longitude))
            latitude = (parsed_json.get('newRows').get('latitude'))
            lat_col.append(str(latitude))
        i = i + 1
    f.close()
    appendToCsv(self, long_col, lat_col)


def sanitizePostcodes(line):
    for char in line:
        if char.isspace():
            line = line
        elif not char.isalnum():
            line = line.replace(char, "")
    return(line)


def appendToCsv(self, long_col, lat_col):
    f = open(self.csvname)
    csv_f = csv.reader(f)
    count = 0
    allRows = []
    for row in csv_f:
        if(count == 0):
            row.append('Longitude')
            row.append('Latitude')
            print(row)
        else:
            row.append(long_col[count-1])
            row.append(lat_col[count-1])
            print(row)
        allRows.append(row)
        count = count + 1
    f.close()
    print("Write New Rows")
    outputFile = open(self.csvname, 'w')
    newRows = pprint.pformat(allRows)
    newRows = re.sub("\[|\]|\'", "", newRows)
    outputFile.write(newRows)
    outputFile.close()
    print("Done")
