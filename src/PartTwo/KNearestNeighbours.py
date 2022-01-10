from datetime import datetime
import math
import matplotlib.pyplot as plt
import csv

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
    if removeOutliers:  # if the outliers are to be removed
        maxAllowedDifference = ph.getOutliersIndex(
            testForOutliers)  # get the max allowed difference before its an outlier
        indexsToRemove = []
        for i in range(len(targetArr)):  # for all the indexes
            if abs(inputArr[i][0] - targetArr[i]) > maxAllowedDifference:
                indexsToRemove.append(i)
        indexsToRemove.sort()#sort the indexes
        count = 0
        for indexToRemove in indexsToRemove:#for all the indexes
            #print("Removing: " + str(inputArr[indexToRemove - count]) + " " + str(targetArr[indexToRemove - count]))
            del inputArr[indexToRemove - count]
            del targetArr[indexToRemove - count]
            count += 1

    return inputArr,targetArr

def getK(maxDataSize,maxK,iterations):
    data,targets = getKNNData(maxDataSize,False)
    seArr = [0] * maxK
    for i in range(0, iterations):
        dataPoint, target = fit.simResult(data, targets)
        for k in range(1,maxK + 1):
            NearestNeighbor = KNearestNeighbour(k)
            knnR = NearestNeighbor.predict(dataPoint)
            seArr[k - 1] += (target-knnR) ** 2
        if (i % int(iterations / 10)) == 0:
            print(str(int(float(i / iterations) * 100)) + "%")
    #recording results
    now = datetime.now()
    with open(appSettings.getPathToKNNFigures() + "KResults" + now.strftime("_%Y%m%d_%H%M%S") + ".csv",
              'w') as f:  # open the file in the write mode
        for k in range(0, maxK):
            seArr[k] = math.sqrt(seArr[k] / iterations)  # set the value to the mean squared value
            f.write(str(k + 1) + "," + str(seArr[k]) + "\n")#write to the file

    #plotting graph
    plt.plot(seArr)
    plt.xlabel("K")
    plt.ylabel("Root Mean Squared Errors")
    plt.savefig(appSettings.getPathToKNNFigures() + "searchingForK" + now.strftime("_%Y%m%d_%H%M%S") + ".png")
    plt.close()

def getKNN():
    return KNearestNeighbour(9)#chose 9 because top is 9 and 8 and 10 are 3rd,4th