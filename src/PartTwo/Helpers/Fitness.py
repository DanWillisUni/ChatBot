import random

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

def simResult(data,targets):
    index = random.randint(0,len(data))
    dataPoint = data[index]
    target = targets[index]
    return dataPoint,target

def getRidData(maxCount):
    connStr = appSettings.getConnStr()
    query = 'SELECT distinct rid from nrch_livst_a51'
    rids = db.runQuery(connStr, query)
    if len(rids) > maxCount:
        rids = rids[:maxCount]  # limit for testing purposes else it takes 4 hours just to load the data
    return rids




