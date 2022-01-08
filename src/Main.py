import random

import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

import matplotlib.pyplot as plt
from datetime import datetime
import time

def getK():
    for k in range(1,100):
        SE = 0
        for delay in range(-5,16):
            for i in range(0,50):
                twoStations = fit.getTwoRandomStations()
                nameA = twoStations[0]
                nameB = twoStations[1]
                simR = fit.simResult(nameA,nameB,delay)
                knnR = knn.getKNNRegression(nameA, nameB, delay,k)
                SE += (simR-knnR) ** 2
                #print("Delayed at " + nameA + " for " + str(delay) + ", estimated lateness to " + nameB + " is " + str(KnnR) + " simlated is " + str(simR))
        print(str(k) + ", " + str(SE))

    plt.plot(SE)
    plt.xlabel("K")
    plt.ylabel("Errors")
    plt.savefig("searchingForK.png")
    plt.close()

def trainNN(maxDataSize,iterations):
    neuralNetwork = nn.NeuralNetwork(0.1)
    neuralNetwork.startTraining(maxDataSize,iterations)
    return neuralNetwork

def compareNNAndKNN(iterationCount):
    neuralNetwork = nn.NeuralNetwork(0.1)
    SEKNN = 0
    SENN = 0
    for i in range(iterationCount):
        twoStations = fit.getTwoRandomStations()
        nameA = twoStations[0]
        nameB = twoStations[1]
        delay = random.randint(-5,20)
        simR = fit.simResult(nameA, nameB, delay)
        knnR = knn.getKNNRegression(nameA, nameB, delay, 5)
        nnR = neuralNetwork.predictNice(delay,nameA,nameB)
        SEKNN += (simR - knnR) ** 2
        SENN += (simR - nnR) ** 2
        if i % (iterationCount/10) == 0:
            print(str(int((100*i)/iterationCount)) + "%")
    print("NN: " + str(SENN/iterationCount))
    print("KNN: " + str(SEKNN / iterationCount))
    return SENN,SEKNN

SENN,SEKNN = compareNNAndKNN(1000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
trainNN(1000,100000)
SENN,SEKNN = compareNNAndKNN(1000)