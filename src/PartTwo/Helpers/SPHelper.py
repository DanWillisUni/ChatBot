import PartTwo.Helpers.DB as DB

def getLatenessFrequencies(connStr,fromStation,toStation,lateby):
    query = "EXEC GetLateness @FromStation = '"+fromStation+"',@ToStation = '"+toStation+"',@LateBy = " + str(lateby)
    result = DB.runQuery(connStr,query)
    return result

def getAllDatatOnStation(connStr,station):
    query = "EXEC GetAllInfoOnStationTimes @station = '" + station + "'"
    result = DB.runQuery(connStr, query)
    return result

def getLatenessFromStations(connStr,fromStation,toStation,rangeStart,rangeEnd):
    query = "EXEC GetLatenessFromStations @FromStation = '" + fromStation +"',@ToStation = '"+toStation+"',@LateByRangeStart = "+str(rangeStart)+",@LateByRangeEnd = " + str(rangeEnd)
    result = DB.runQuery(connStr, query)
    return result

def getLatenessOfBoth(connStr, fromStation, toStation):
    query = "EXEC GetLatenessOfBoth @FROM = '" + fromStation + "',@TO = '" + toStation + "'"
    result = DB.runQuery(connStr, query)
    return result

def compareStations(connStr, A, B):
    query = "EXEC CompareStations @A = '" + A + "',@B = '" + B + "'"
    result = DB.runQuery(connStr, query)
    return result[0][:-2]

def getLatenessFromRID(connStr,RID):
    query = "EXEC GetLatenessFromRID @rid = '" + RID + "'"
    result = DB.runQuery(connStr, query)
    return result