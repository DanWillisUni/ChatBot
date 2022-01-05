import PartTwo.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

def getK():
    for k in range(1,100):
        SE = 0
        for i in range(-5,16):
            for a in range(0,50):
                twoStations = fit.getTwoRandomStations()
                nameA = twoStations[0]
                nameB = twoStations[1]
                simR = fit.simResult(nameA,nameB,i)
                knnR = knn.getKNNRegression(nameA, nameB, i,k)
                SE += abs(simR-knnR) ** 2
                #print("Delayed at " + nameA + " for " + str(i) + ", estimated lateness to " + nameB + " is " + str())
        print(str(k) + ", " + str(SE))


def trainNN():
    inputs, targets = fit.getNNData()
    neural_network = nn.NeuralNetwork(0.1)
    neural_network.train(inputs,targets,1)

trainNN()