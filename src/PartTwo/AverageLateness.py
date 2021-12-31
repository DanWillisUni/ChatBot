import DB
def getAverageLateness(connStr,fromStation,toStation,lateby):
    query = "EXEC GetAverageLateness @FromStation = '"+fromStation+"',@ToStation = '"+toStation+"',@LateBy = -" + str(lateby)
    result = DB.runQuery(connStr,query)[0].replace(", ","")
    if(result == 'None'):
        result = '-1'
    return 0-int(result)