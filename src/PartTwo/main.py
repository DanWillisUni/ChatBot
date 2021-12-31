import AverageLateness
import DB

connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;"
#connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Charlies
#connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Brandons

print(AverageLateness.getAverageLateness(connStr,"SOTON","WATRLMN",10))

'''stations = DB.runQuery(connStr,"EXEC LookupStation @searchTerm = 'LONDON'")
for station in stations:
    print(station.split(",")[0])'''