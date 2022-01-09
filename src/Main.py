import math

import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

def compareNNAndKNN(iterationCount):
    neuralNetwork = nn.getNN()
    nearestNeighbor = knn.getKNN()
    data,targets = knn.getKNNData(1000,True)
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

def compareWithTrain(iterationCount):
    results = []
    for i in range(iterationCount):
        NN, KNN = compareNNAndKNN(100)
        nn.trainNN(1000, 10000)
        results.append([NN,KNN])
    NN, KNN = compareNNAndKNN(100)
    results.append([NN, KNN])

    for i in results:
        #print("NN: " + str(i[0]))
        #print("KNN: " + str(i[1]))
        print("VS: " + str(i[0]/i[1]))#if this is less than 1 then the NN is better than KNN

knn.getK(1000,100,1000)

compareWithTrain(100)