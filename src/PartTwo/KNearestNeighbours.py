import math
import matplotlib.pyplot as plt

import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.Fitness as fit
import PartTwo.Helpers.ProbabilityHelper as ph

class KNearestNeighbour:
    def __init__(self,k):
        self.k = k

    def knn(self, data, query, distanceFunction):
        neighborDistancesAndIndices = []
        for index, d in enumerate(data):
            distance = distanceFunction(d[:-1], query)
            neighborDistancesAndIndices.append((distance, index))# Add the distance and the index of the data to an ordered collection
        sortedNeighborDistancesAndIndices = sorted(neighborDistancesAndIndices)# Sort the ordered collection of distances and indices from smallest to largest (in ascending order) by the distances
        kNearestDistancesAndIndices = sortedNeighborDistancesAndIndices[:self.k]# Pick the first K entries from the sorted collection
        kNearestLabels = [data[i][-1] for distance, i in kNearestDistancesAndIndices]#Get the labels of the selected K entries

        return kNearestDistancesAndIndices, self.mean(kNearestLabels)

    def mean(self,labels):
        return sum(labels) / len(labels)

    def euclidean_distance(self,point1, point2):
        sumSquaredDistance = 0
        for i in range(len(point1)):
            sumSquaredDistance += math.pow(point1[i] - point2[i], 2)
        return math.sqrt(sumSquaredDistance)

    def predict(self,datapoint):
        return self.predictNice(datapoint[1],datapoint[2],datapoint[0])

    def predictNice(self,fromStationTPL,toStationTPL,delay):
        connStr = appSettings.getConnStr()
        all = sph.getLatenessOfBoth(connStr, fromStationTPL, toStationTPL)
        if len(all) == 0:
            return delay
        else:
            reg_data = []
            for i in all:
                lineList = []
                lineList.append(int(i.split(",")[0]))
                lineList.append(int(i.split(",")[1]))
                reg_data.append(lineList)
            reg_query = [delay]
            reg_k_nearest_neighbors, reg_prediction = self.knn(
                reg_data, reg_query, distanceFunction=self.euclidean_distance
            )
            return reg_prediction

def getKNNData(maxCount,removeOutliers):
    connStr = appSettings.getConnStr()
    rids = fit.getRidData(maxCount)
    inputArr = []
    targetArr = []
    testForOutliers = []
    for rid in rids:
        rid = rid.replace(" ', ", "")[1:]
        ridData = sph.getLatenessFromRID(connStr, rid)
        for a in range(len(ridData)):
            nameA = ridData[a].split(",")[0].replace(" ", "").replace("'", "")
            delayA = int(ridData[a].split(",")[1])
            for b in range(a + 1, len(ridData)):
                nameB = ridData[b].split(",")[0].replace(" ", "").replace("'", "")
                delayB = int(ridData[b].split(",")[1])
                inputArr.append([delayA,nameA,nameB])
                targetArr.append(delayB)
                testForOutliers.append(abs(delayA-delayB))
    if removeOutliers:
        indexsToRemove = ph.getOutliersIndex(testForOutliers)
        for indexToRemove in indexsToRemove:
            del inputArr[indexToRemove]
            del targetArr[indexToRemove]
    return inputArr,targetArr

def getK(maxDataSize,maxK,iterations):
    data,targets = getKNNData(maxDataSize,True)
    mse = []
    for k in range(1,maxK + 1):
        SE = 0
        NearestNeighbor = KNearestNeighbour(k)
        for i in range(0,iterations):
            dataPoint,target = fit.simResult(data, targets)
            knnR =  NearestNeighbor.predict(dataPoint)
            SE += (target-knnR) ** 2
            #print("Delayed at " + nameA + " for " + str(delay) + ", estimated lateness to " + nameB + " is " + str(KnnR) + " simlated is " + str(simR))
        print(str(k) + ", " + str(SE))
        mse.append(SE/iterations)

    plt.plot(mse)
    plt.xlabel("K")
    plt.ylabel("Errors")
    plt.savefig("../resources/PartTwo/KNNGraphs/searchingForK.png")
    plt.close()