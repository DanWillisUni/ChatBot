import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

def compareNNAndKNN(iterationCount):
    neuralNetwork = nn.NeuralNetwork(0.1)
    nearestNeighbor = knn.KNearestNeighbour(5)
    data,targets = knn.getKNNData(100,True)
    SEKNN = 0
    SENN = 0
    for i in range(iterationCount):
        dataPoint,target = fit.simResult(data, targets)
        knnR = nearestNeighbor.predict(dataPoint)
        nnR = neuralNetwork.predictNice(dataPoint[0],dataPoint[1],dataPoint[2])
        SEKNN += (target - knnR) ** 2
        SENN += (target - nnR) ** 2
        #print(nnR)
        if i % (iterationCount/10) == 0:
            print(str(int((100*i)/iterationCount)) + "%")
    print("NN: " + str(SENN/iterationCount))
    print("KNN: " + str(SEKNN / iterationCount))
    return SENN,SEKNN

#knn.getK(1000,100,1000)

#nn.trainNN(1000,500000)

compareNNAndKNN(100)
nn.trainNN(100,100000)
compareNNAndKNN(100)