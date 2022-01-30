import pyodbc

def run_query(conn_str, query):
    """
    Run sql query and return the results as a string array

    :param conn_str:
    The connection string to the server/database
    :param query:
    The SQL query to run

    :return:
    A string array of the results from the SQL query
    """
    r = []  #set the result array to empty
    cnxn = pyodbc.connect(r'Driver={SQL Server};' + conn_str)  # get connection
    cursor = cnxn.cursor()
    cursor.execute(query)  # execute the query
    while 1:  # while true
        row = cursor.fetchone()  # fetch the next row of the results
        if not row:  # if the next line isnt a row
            break  # break the while loop
        r.append(converter(row.__str__()))  # add the row to the results string array
    cnxn.close()  # close the connection
    return r


def converter(str_in):
    """
    Converter to convert the row string to a more readable format

    :param str_in:
    The string of the row

    :return:
    String reformatted
    """
    return str_in[1:-1].replace(", None", ", Null")
