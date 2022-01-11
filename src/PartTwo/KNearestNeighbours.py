from datetime import datetime
import math
import matplotlib.pyplot as plt

import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.Fitness as fit
import PartTwo.Helpers.ProbabilityHelper as ph


class KNearestNeighbour:
    def __init__(self, k):
        """
        Initilise the KNN object

        :param k:
        The K value for the object
        """
        self.k = k

    def knn(self, data, query, distanceFunction):
        """
        Calculates the prediction and the nearest neighbors

        :param data:
        All the data about both stations
        :param query:
        The amount the train is delayed by at the first station
        :param distanceFunction:
        The distance function used (I used euclidean)
        :return:
        Array of the nearest Neighbors
        Prediction based on the neighbors
        """
        neighborDistancesAndIndices = []  # initilise the array of neighbors
        for index, d in enumerate(data):  # for each in data
            distance = distanceFunction(d[:-1], query)  # gets the distance between the datas delay and the querys delay
            neighborDistancesAndIndices.append(
                (distance, index))  # Add the distance and the index of the data to an ordered collection
        sortedNeighborDistancesAndIndices = sorted(
            neighborDistancesAndIndices)  # Sort the ordered collection of distances and indices from smallest to largest (in ascending order) by the distances
        kNearestDistancesAndIndices = sortedNeighborDistancesAndIndices[
                                      :self.k]  # Pick the first K entries from the sorted collection
        kNearestLabels = [data[i][-1] for distance, i in
                          kNearestDistancesAndIndices]  # Get the labels of the selected K entries

        return kNearestDistancesAndIndices, mean(kNearestLabels)

    def predict(self, datapoint):
        """
        Predict the delay at station B

        :param datapoint:
        Array containing the delay at station A, the name of station A and the name of station B
        :return:
        Prediction of mins late to station B
        """
        return self.predictNice(datapoint[0], datapoint[1],
                                datapoint[2])  # split the data and use the predictNice function
    def predictNice(self, delay, fromStationTPL, toStationTPL):
        """
        Predicts the delay to station B

        This function should be used in the chat bot as it is easier to get the data into

        :param delay:
        The delay at the first station
        :param fromStationTPL:
        The name of the first station
        :param toStationTPL:
        The name of the second station
        :return:
        The prediction
        """
        connStr = appSettings.getConnStr()  # get the connection string
        all = sph.getLatenessOfBoth(connStr, fromStationTPL, toStationTPL)  # get all the data about the two stations
        if len(all) == 0:  # if there is no data
            return delay  # return the delay
        else:
            data = []
            for i in all:#for all the data
                lineList = []
                lineList.append(int(i.split(",")[0]))#add the delay to first to the line array
                lineList.append(int(i.split(",")[1]))#add the delay to second to the line array
                data.append(lineList)#add the line array to the data
            query = [delay]#set the query to the delay
            kNearestNeighbors, prediction = self.knn(data, query, distanceFunction=euclideanDistance)#call the prediction function
            return prediction

# Static functions KNN specific
def mean(labels):
    """
    Get the mean of the values in the array

    :param labels:
    Array of values
    :return:
    The mean of the values
    """
    return sum(labels) / len(labels)#get the mean
def euclideanDistance(point1, point2):
    """
    Calculate the eulidean distance between 2 points

    :param point1:

    :param point2:
    :return:
    """
    sumSquaredDistance = 0
    for i in range(len(point1)):  # for all the values in the point
        sumSquaredDistance += math.pow(point1[i] - point2[i], 2)  # square the difference and add it to the sum
    return math.sqrt(sumSquaredDistance)  # square root the sum

def getKNNData(maxCount, removeOutliers):
    """
    Get all the data for the KNN

    :param maxCount:
    Number of RIDs to proccess
    :param removeOutliers:
    Bool if the outliers should be removed
    :return:
    All the data for the KNN
    """
    connStr = appSettings.getConnStr()  # get the database connectionString
    rids = fit.getRidData(maxCount)  # get all the RIDs inside the maxCount
    inputArr = []
    targetArr = []
    testForOutliers = []
    for rid in rids:  # for each RID
        rid = rid.replace(" ', ", "")[1:]
        ridData = sph.getLatenessFromRID(connStr, rid)  # get all the data from the RID
        for a in range(len(ridData)):  #for all the data in the rid data
            nameA = ridData[a].split(",")[0].replace(" ", "").replace("'", "")  #get the station name
            delayA = int(ridData[a].split(",")[1])  #get the delay at station A
            for b in range(a + 1, len(ridData)):  #for all the stations after the station A
                nameB = ridData[b].split(",")[0].replace(" ", "").replace("'", "")  #set the station B name
                delayB = int(ridData[b].split(",")[1])  #set the station B delay
                inputArr.append([delayA, nameA, nameB])  #add data to the input array
                targetArr.append(delayB)  #add data to the target array
                testForOutliers.append(abs(delayA - delayB))  #add the differnce to the outlier test array
    if removeOutliers:  # if the outliers are to be removed
        maxAllowedDifference = ph.getOutliersMin(testForOutliers)  # get the max allowed difference before its an outlier
        indexsToRemove = []
        for i in range(len(targetArr)):  # for all the indexes
            if abs(inputArr[i][0] - targetArr[i]) > maxAllowedDifference:
                indexsToRemove.append(i)
        indexsToRemove.sort()  # sort the indexes
        count = 0
        for indexToRemove in indexsToRemove:  # for all the indexes
            # print("Removing: " + str(inputArr[indexToRemove - count]) + " " + str(targetArr[indexToRemove - count]))
            del inputArr[indexToRemove - count]  #delete the entry
            del targetArr[indexToRemove - count]  #delete the entry
            count += 1

    return inputArr, targetArr


def getK(maxDataSize, maxK, iterations):
    """
    Test to find the best value of K

    This function doesnt need to be run again but I have left it included

    :param maxDataSize:
    Number of RIDs to proccess
    :param maxK:
    Max number to iterate to from 1
    :param iterations:
    Number of iterations to be done

    :return:
    Plots a graph of the data for all the k values
    Writes the results to a csv file
    """
    data, targets = getKNNData(maxDataSize, False)  #get all the data
    seArr = [0] * maxK  #set up the results array
    for i in range(0, iterations):  #for each iteration
        dataPoint, target = fit.simResult(data, targets)  #select a random peice of data and target
        for k in range(1, maxK + 1):  #for each K value
            NearestNeighbor = KNearestNeighbour(k)  #generate a new instance with the k value
            knnR = NearestNeighbor.predict(dataPoint)  #predict on the data
            seArr[k - 1] += (target - knnR) ** 2  #square the difference between prediction and target and add to sum
        if (i % int(iterations / 10)) == 0:  #if it is a multipule of 10 percent of the way through
            print(str(int(float(i / iterations) * 100)) + "%")  #print the percentage of the way through
    # recording results
    now = datetime.now()#get the time now
    with open(appSettings.getPathToKNNFigures() + "KResults" + now.strftime("_%Y%m%d_%H%M%S") + ".csv",
              'w') as f:  # open the file in the write mode
        for k in range(0, maxK):
            seArr[k] = math.sqrt(seArr[k] / iterations)  # set the value to the mean squared value
            f.write(str(k + 1) + "," + str(seArr[k]) + "\n")  # write to the file

    # plotting graph
    plt.plot(seArr)
    plt.xlabel("K")
    plt.ylabel("Root Mean Squared Errors")
    plt.savefig(appSettings.getPathToKNNFigures() + "searchingForK" + now.strftime("_%Y%m%d_%H%M%S") + ".png")
    plt.close()

def getKNN():
    """
    Gets a new object of the KNN class

    This sets the K value up which was found using the getK function above

    :return:
    A new KNN object
    """
    return KNearestNeighbour(9)  # chose 9 because top is 9 and 8 and 10 are 3rd,4th
