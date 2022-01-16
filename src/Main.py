import math
import matplotlib.pyplot as plt
from datetime import datetime

import numpy as np

import PartTwo.Bayes
import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

def compareNNAndKNN(iterationCount,dataLimit):
    neuralNetwork = nn.getNN()
    nearestNeighbor = knn.getKNN()
    data,targets = knn.getKNNData(dataLimit,True)
    SEKNN = 0
    SENN = 0
    for i in range(iterationCount):
        dataPoint,target = fit.simResult(data, targets)
        knnR = nearestNeighbor.predict(dataPoint)
        nnR = neuralNetwork.predictNice(dataPoint[0],dataPoint[1],dataPoint[2])
        SEKNN += (target - knnR) ** 2
        SENN += (target - nnR) ** 2
        if i % (iterationCount/10) == 0:
            print(str(int((100*i)/iterationCount)) + "%")
    print("NN: " + str(math.sqrt(SENN / iterationCount)))
    print("KNN: " + str(math.sqrt(SEKNN / iterationCount)))
    return math.sqrt(SENN / iterationCount),math.sqrt(SEKNN / iterationCount)

def compareWithTrain(iterationCount,dataLimit,trainingIterations,compareIterations):
    nnPlot = []
    knnPlot = []
    trainingError = []
    for i in range(iterationCount):
        NN, KNN = compareNNAndKNN(compareIterations,dataLimit)
        toAdd = nn.trainNN(dataLimit, trainingIterations)
        for ta in toAdd:
            trainingError.append(ta)
        nnPlot.append(NN)
        knnPlot.append(KNN)
        print("COMP: " + str(i) + "/" + str(iterationCount))

    NN, KNN = compareNNAndKNN(compareIterations,dataLimit)
    nnPlot.append(NN)
    knnPlot.append(KNN)

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

    plt.plot(trainingError)
    plt.yscale('linear')
    plt.grid(True)
    plt.xlabel("Iterations (thousands)")
    plt.ylabel("Root Mean square error in all training instances")
    plt.savefig("FullTrainingData_" + datetime.now().strftime("%Y%m%d_%H%M%S_") + ".png")
    plt.close()

#knn.getK(1000,100,1000) # ~12 hours

compareWithTrain(20,1000,100000,1000)#one hour per iteration