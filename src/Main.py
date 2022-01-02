import Stations.findStations as fs
stationsFound = fs.searchStations("SOTON")
for s in stationsFound:
    print(s.toString())
