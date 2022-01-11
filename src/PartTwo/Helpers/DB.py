import pyodbc

def runQuery(connStr,query):
    """
    Run sql query and return the results as a string array

    :param connStr:
    The connection string to the server/database
    :param query:
    The SQL query to run

    :return:
    A string array of the results from the SQL query
    """
    r = []  #set the result array to empty
    cnxn = pyodbc.connect(r'Driver={SQL Server};' + connStr)  #get connection
    cursor = cnxn.cursor()
    cursor.execute(query)  #execute the query
    while 1:  #while true
        row = cursor.fetchone()  #fetch the next row of the results
        if not row:  #if the next line isnt a row
            break  #break the while loop
        r.append(converter(row.__str__()))  #add the row to the results string array
    cnxn.close()  #close the connection
    return r

def converter(strIn):
    """
    Converter to convert the row string to a more readable format

    :param strIn:
    The string of the row

    :return:
    String reformatted
    """
    return strIn[1:-1].replace(", None",", Null")