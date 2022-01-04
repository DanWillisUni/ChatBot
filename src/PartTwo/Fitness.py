import random

import PartTwo.SPHelper as sph
import appSettings
import PartTwo.KNearestNeighbours as knn

def simResult(fromStation,toStation,delay):
    frequencies = sph.getLatenessFromStations(appSettings.getConnStr(), fromStation,toStation, delay, delay)
    if len(frequencies) > 0:
        sum = 0;
        for i in frequencies:
            sum += int((i.split(",")[1]))
        randIndex = random.randint(0, sum + 1)
        for i in frequencies:
            randIndex -= int((i.split(",")[1]))
            if randIndex < 0:
                return int((i.split(",")[0]))
    return delay

def getK():
    for k in range(1,100):
        differance = 0
        for i in range(-5,16):
            for a in range(0,50):
                nameA = 'SOTON'
                nameB = 'WATRLMN'
                simR = simResult(nameA,nameB,i)
                knnR = knn.getKNNRegression(nameA, nameB, i,k)
                differance += abs(simR-knnR)
                #print("Delayed at " + nameA + " for " + str(i) + ", estimated lateness to " + nameB + " is " + str())
        print(str(k) + ", " + str(differance))