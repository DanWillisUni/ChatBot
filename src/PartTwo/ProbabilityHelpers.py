import DB
def getLatenessFrequencies(connStr,fromStation,toStation,lateby):
    query = "EXEC GetLateness @FromStation = '"+fromStation+"',@ToStation = '"+toStation+"',@LateBy = " + str(lateby)
    result = DB.runQuery(connStr,query)
    return result