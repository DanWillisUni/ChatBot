import PartTwo.Helpers.DB as DB

def getAllDatatOnStation(connStr,station):
    """
    Runs the GetAllInfoOnStationTimes stored procedure with the parameters

    :param connStr:
    Connection string to the Server/Database
    :param station:
    Station name to get all the data on
    :return:
    The results for the SP
    """
    query = "EXEC GetAllInfoOnStationTimes @station = '" + station + "'"  #sets the query string
    result = DB.runQuery(connStr, query)  #execute the stored procedure
    return result

def getLatenessFromStations(connStr,fromStation,toStation,rangeStart,rangeEnd):
    """
    Runs the GetLatenessFromStations stored procedure with the parameters

    :param connStr:
    Connection string of the server/database
    :param fromStation:
    The station A
    :param toStation:
    The station B
    :param rangeStart:
    The range of late by start
    :param rangeEnd:
    The range of late by end
    :return:
    String array of all the rows from the query
    """
    query = "EXEC GetLatenessFromStations @FromStation = '" + fromStation +"',@ToStation = '"+toStation+"',@LateByRangeStart = "+str(rangeStart)+",@LateByRangeEnd = " + str(rangeEnd)  # generate query
    result = DB.runQuery(connStr, query)  #run the query
    return result

def getLatenessOfBoth(connStr, fromStation, toStation):
    """
    Executes the GetLatenessOfBoth stored procedure

    :param connStr:
    The connection string to the server/database
    :param fromStation:
    The Station A name
    :param toStation:
    The station B name
    :return:
    String array of the result rows
    """
    query = "EXEC GetLatenessOfBoth @FROM = '" + fromStation + "',@TO = '" + toStation + "'"  # generate the query string
    result = DB.runQuery(connStr, query)  #run the query on the database
    return result

def compareStations(connStr, A, B):
    """
    Executes the CompareStations stored procedure with parameters

    :param connStr:
    Connection string to database/Server
    :param A:
    Station Name A
    :param B:
    Station Name B

    :return:
    String array of the rows of results
    """
    query = "EXEC CompareStations @A = '" + A + "',@B = '" + B + "'"  # generate the query
    result = DB.runQuery(connStr, query)  # run the query
    return result[0][:-2]

def getLatenessFromRID(connStr,RID):
    """
    Execute the GetLatenessFromRID stored procedure

    :param connStr:
    Connection string to the database or server
    :param RID:
    Route ID to search

    :return:
    String array of the result rows
    """
    query = "EXEC GetLatenessFromRID @rid = '" + RID + "'"  # get the query string
    result = DB.runQuery(connStr, query)  # run the query
    return result