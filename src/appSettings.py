def get_conn_str():
    connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;"
    # connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Charlies
    # connStr = "Server=DANS-LATITUDE\SQLEXPRESS;Database=AIChatBot;Trusted_Connection=yes;" Brandons
    return connStr


def get_nn_save_path():
    return "../resources/PartTwo/FindingCorrectValue/currentSave"


def get_station_compare_path():
    return "../resources/PartTwo/comparingStations.txt"


def get_path_to_knn_figures():
    return "../resources/PartTwo/KNNGraphs/"


def get_path_to_nn_figures():
    return "../resources/PartTwo/NNGraphs/"


def get_API():
    #return "fb"
    return "api"
    #return "console"
