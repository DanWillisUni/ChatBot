import DB
connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;"
query = "SELECT * FROM Stations"

Stations = DB.runQuery(query, connStr)
for s in Stations:
    print(s)