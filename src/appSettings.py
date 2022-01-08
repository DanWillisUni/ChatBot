def getConnStr():
    connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;"
    # connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Charlies
    # connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Brandons
    return connStr

def getCurrentSavePath():
    return "../resources/PartTwo/currentSave.txt"
def getStationComparePath():
    return "../resources/PartTwo/comparingStations.txt"

