import random

import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.DB as db

def getAllStations():
    """
    Select all the stations from the database

    :return:
    String array of distinct station names
    """
    r = []
    connStr = appSettings.getConnStr()  #get the connection string
    query = "SELECT distinct (tpl) FROM nrch_livst_a51 where pta is not null or ptd is not null or arr_at is not null or dep_at is not null"  #set the query
    result = db.runQuery(connStr,query)  #run the query on the database
    for i in result:  # for all the station rows
        r.append(i.split(",")[0].replace(" ","").replace("'",""))#format the string to get
    return r

def simResult(data,targets):
    """
    Simulate a random result in the dataset

    :param data:
    all the datasets
    :param targets:
    all the matching targets

    :return:
    A random datapoint and matching target
    """
    index = random.randint(0,len(data) -1)  # random dataset
    dataPoint = data[index]  #set the datapoint
    target = targets[index]  #set the matching target result
    return dataPoint,target

def getRidData(maxCount):
    """
    Get the top RIDs from the data

    :param maxCount:
    Max number of RIDs to return
    :return:
    Array of RIDs from the database
    """
    connStr = appSettings.getConnStr()  # get the connection string
    query = 'SELECT distinct rid from nrch_livst_a51'  # set the query
    rids = db.runQuery(connStr, query)  #execute the query
    if len(rids) > maxCount:  #if the array is longer than the 
        rids = rids[:maxCount]  # limit else it takes 4 hours just to load the data
    return rids