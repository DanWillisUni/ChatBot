import random
import numpy as np
from os.path import exists

import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.DB as db

def getAllStations():
    r = []
    connStr = appSettings.getConnStr()
    query = "SELECT distinct (tpl) FROM nrch_livst_a51 where pta is not null or ptd is not null or arr_at is not null or dep_at is not null"
    result = db.runQuery(connStr,query)
    for i in result:
        r.append(i.split(",")[0].replace(" ","").replace("'",""))
    return r

def getTwoRandomStations():
    connStr = appSettings.getConnStr()
    query = 'SELECT distinct rid from nrch_livst_a51'
    rids = db.runQuery(connStr, query)
    attemptAnotherRid = True
    while attemptAnotherRid:
        randRid = rids[random.randint(0,len(rids) - 1)].replace(" ', ","")[1:]
        query2 = 'SELECT tpl, (CASE WHEN pta IS NOT NULL THEN pta WHEN ptd IS NOT NULL AND pta IS NULL THEN ptd WHEN arr_at IS NOT NULL AND ptd IS NULL AND pta IS NULL THEN arr_at ELSE dep_at END) as time FROM nrch_livst_a51 where rid = \'' + randRid + '\' and (arr_at IS NOT NULL or ptd IS NOT NULL OR pta IS NOT NULL OR dep_at IS NOT NULL)'
        stations = db.runQuery(connStr, query2)
        if len(stations) > 1:
            attemptAnotherRid = False

    a = stations[random.randint(0,len(stations) - 1)]
    b = stations[random.randint(0, len(stations) - 1)]
    while a == b:
        b = stations[random.randint(0, len(stations) - 1)]
    aName = a.split(",")[0].replace(" ","").replace("'","")
    bName = b.split(",")[0].replace(" ", "").replace("'", "")

    comp = sph.compareStations(connStr,aName,bName)
    if int(comp) > 0:
        return [aName,bName]
    return [bName, aName]

def simResult(fromStation,toStation,delay):
    frequencies = sph.getLatenessFromStations(appSettings.getConnStr(), fromStation,toStation, delay, delay)
    if len(frequencies) > 0:
        sum = 0;
        for i in frequencies:
            sum += int((i.split(",")[1]))
        randIndex = random.randint(0, sum + 1)
        for i in frequencies:
            randIndex -= int((i.split(",")[1]))
            if randIndex < 0:
                return int((i.split(",")[0]))
    return delay

def getStationCompareIndex(stationDic, A, B):
    return (stationDic[A] * 77) + stationDic[B]

def getStationCompare():
    allStations = getAllStations()
    stationDic = {}
    for i in range(len(allStations)):
        stationDic[allStations[i]] = i

    if exists(appSettings.getStationComparePath()):
        f = open(appSettings.getStationComparePath(), "r")
        content = f.read()
        comparingStations = content.splitlines()
        f.close()
    else:
        comparingStations = [None] * 5929
        for a in range(len(allStations)):
            nameA = allStations[a]
            for b in range(a + 1, len(allStations)):
                nameB = allStations[b]
                normalDistance = sph.compareStations(appSettings.getConnStr(), nameA, nameB)
                if normalDistance != 'None':
                    comparingStations[getStationCompareIndex(stationDic,nameA, nameB)] = int(normalDistance)
                    comparingStations[getStationCompareIndex(stationDic,nameB, nameA)] = 0 - int(normalDistance)
        with open(appSettings.getStationComparePath(), 'w') as f:
            for item in comparingStations:
                f.write("%s\n" % item)
    return comparingStations,stationDic

def getNNData(maxDataSize):
    connStr = appSettings.getConnStr()
    comparingStations,stationDic = getStationCompare()
    query = 'SELECT distinct rid from nrch_livst_a51'
    rids = db.runQuery(connStr, query)
    if len(rids) > maxDataSize:
        rids = rids[:maxDataSize]#limit for testing purposes else it takes 4 hours just to load the data
    inputs = np.empty(shape=[0,2],dtype=int)
    targets = np.empty(shape=[0],dtype=int)
    for rid in rids:
        rid = rid.replace(" ', ","")[1:]
        ridData = sph.getLatenessFromRID(connStr,rid)
        for a in range(len(ridData)):
            nameA = ridData[a].split(",")[0].replace(" ","").replace("'","")
            delayA = int(ridData[a].split(",")[1])
            for b in range(a + 1,len(ridData)):
                nameB = ridData[b].split(",")[0].replace(" ","").replace("'","")
                delayB = int(ridData[b].split(",")[1])
                #if abs(delayA -delayB) < 15:#removing outliers
                input = np.array([delayA, int(comparingStations[getStationCompareIndex(stationDic,nameA, nameB)])])
                inputs = np.vstack((inputs,input))
                targets = np.append(targets,delayB)
                #else:
                    #print(str(delayA) + "," + str(delayB))
    return inputs,targets
