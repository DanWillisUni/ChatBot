import PartTwo.DB as DB
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