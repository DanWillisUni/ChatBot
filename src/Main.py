import PartTwo.KNearestNeighbours as knn
import PartTwo.DB as db
import appSettings
import PartTwo.Fitness as fit

def getMaxNumStations():
    query = 'WITH CTE as (SELECT ROW_NUMBER() OVER(PARTITION BY rid ORDER BY (CASE WHEN pta IS NOT NULL THEN pta ELSE ptd END) ASC) AS Row#,	rid,tpl FROM nrch_livst_a51 where (pta is not null or ptd is not null)) SELECT tpl FROM CTE WHERE rid = (SELECT MAX(rid) FROM CTE WHERE Row# = (SELECT MAX(Row#) FROM CTE)) order by Row# asc'

    listOfStationNames = db.runQuery(appSettings.getConnStr(),query)
    for k in range(1,100):
        differance = 0
        for i in range(-2,11):
            for a in range(0,len(listOfStationNames)):
                nameA = listOfStationNames[a][1:-4]
                for b in range(a+1,len(listOfStationNames)):
                    nameB = listOfStationNames[b][1:-4]
                    simR = fit.simResult(nameA,nameB,i)
                    knnR = knn.getKNNRegression(nameA, nameB, i)
                    differance += abs(simR-knnR)
                    #print("Delayed at " + nameA + " for " + str(i) + ", estimated lateness to " + nameB + " is " + str())
        print(k + ": " + differance)

getMaxNumStations()
