import math
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

def compareNNAndKNN(iterationCount):
    """
    Compares the KNN with the NN

    :param iterationCount:
    How many iterations to test over
    :return:
    How accurate the NN and the KNN were on average
    """
    neuralNetwork = nn.getNN()  #get the neaural Network
    nearestNeighbor = knn.getKNN()  # get the k nearest neighbor object
    data,targets = knn.getKNNData(1000,True)  #load some data up
    SEKNN = 0  #set the sum of KNN error to 0
    SENN = 0  #set the sum of the NN error to 0
    for i in range(iterationCount):  # for each iteration
        dataPoint,target = fit.simResult(data, targets)  # simulate result
        knnR = nearestNeighbor.predict(dataPoint)  #get the knn prediction
        nnR = neuralNetwork.predictNice(dataPoint[0],dataPoint[1],dataPoint[2])  # get the nn prediction
        SEKNN += (target - knnR) ** 2  # square the differnce of the knn result to the actual and add it to the sum
        SENN += (target - nnR) ** 2  # square the differnce of the nn result to the actual and add it to the sum
        if i % (iterationCount/10) == 0:  #if the iteration is a multipule of 10 percent of the way through
            print(str(int((100*i)/iterationCount)) + "%")  #print the percentage
    print("NN: " + str(math.sqrt(SENN / iterationCount)))  #print results for neural Network
    print("KNN: " + str(math.sqrt(SEKNN / iterationCount)))  # print results for the k nearest neighbor
    return math.sqrt(SENN / iterationCount),math.sqrt(SEKNN / iterationCount)  #return the results

def compareWithTrain(iterationCount):
    """
    Compare the NN while training it

    :param iterationCount:
    Number of iterations to run for
    :return:
    Chart of the results
    """
    nnPlot = []
    knnPlot = []
    for i in range(iterationCount):  #for each iteration
        NN, KNN = compareNNAndKNN(1000)  #compare the nn and knn
        nn.trainNN(1000, 100000)  #train the nn
        nnPlot.append(NN)  #add to the results for nn
        knnPlot.append(KNN)  #add to the results for the knn
        if (i % int(iterationCount / 10)) == 0:  # if the iteration is a multiplue of 10 percent of the way through
            print("COMP" + str(int(float(i / iterationCount) * 100)) + "%")  #print the percentage of the way through

    NN, KNN = compareNNAndKNN(1000)  #do a final comparison
    nnPlot.append(NN)  #add the results for nn
    knnPlot.append(KNN)  #add the results for the knn

    # plotting graph
    plt.plot(nnPlot, label="Neural Network")
    plt.plot(knnPlot, label="K Nearest Neighbor")
    plt.yscale('linear')
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.xlabel("Iterations of NN training (100 thousand)")
    plt.ylabel("Root Mean square error of KNN over NN")
    plt.savefig("Comparison" + datetime.now().strftime("_%Y%m%d_%H%M%S") + ".png")
    plt.close()

#knn.getK(1000,100,1000) # ~12 hours

compareWithTrain(20)# ~ 75 mins per iteration