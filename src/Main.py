import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn

import matplotlib.pyplot as plt
from datetime import datetime

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

def trainNN(maxDataSize,iterations):
    neural_network = nn.NeuralNetwork(0.1)
    inputs, targets = neural_network.getNNData(maxDataSize)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Finish Data load=", current_time)
    training_error = neural_network.train(inputs,targets,iterations)#~5000 iter per min
    plt.plot(training_error)
    plt.xlabel("Iterations (hundreds)")
    plt.ylabel("Error for all training instances")
    now = datetime.now()
    plt.savefig("../resources/PartTwo/NNGraphs/" + now.strftime("%Y%m%d_%H%M%S_") + str(maxDataSize)+ ".png")

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Start Time =", current_time)
trainNN(100,1000)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("End Time =", current_time)