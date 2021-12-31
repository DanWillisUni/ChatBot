import pyodbc
import Stations

def runQuery(query,connStr):
    r = []
    cnxn = pyodbc.connect(r'Driver={SQL Server};' + connStr)
    cursor = cnxn.cursor()
    cursor.execute(query)
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        r.append(converter(row.__str__()))
    cnxn.close()
    return r

def converter(strIn):
    return strIn[1:-1].replace(", None",", Null")