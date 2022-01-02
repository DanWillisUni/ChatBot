import csv
from Stations.Station import Station
import re

def loadStations():
    with open('../resources/stations.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        lines = []
        for row in spamreader:
            lines.append(('[\"' + '\", \"'.join(row) + '\"]').replace("\\N","NULL").replace("'","\\'"))
    stationArr = []
    for i in range(1,len(lines)):
        stationLineArr = eval(lines[i])
        stationArr.append(Station(stationLineArr))
    return stationArr

def isTermInStation(term,station):
    if len(re.findall(term,station.toString())) > 0:
        return True
    return False

def searchStations(searchTerm):
    allStations = loadStations()
    r = []
    regTerm = ""
    for c in searchTerm:
        regTerm += "[" + str(c).upper() + "|" + str(c).lower() +"]"
        regTerm += "[A-Z|a-z]*"
    regTerm += "[^;]*;"
    for s in allStations:
        if isTermInStation(regTerm,s):
            r.append(s)
    return r