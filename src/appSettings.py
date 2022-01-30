def get_conn_str():
    connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;"
    # connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Charlies
    # connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Brandons
    return connStr

def getNNCurrentSavePath():
    return "../resources/PartTwo/currentSave"
def getStationComparePath():
    return "../resources/PartTwo/comparingStations.txt"
def getPathToKNNFigures():
    return "../resources/PartTwo/KNNGraphs/"
def getPathToNNFigures():
    return "../resources/PartTwo/NNGraphs/"

