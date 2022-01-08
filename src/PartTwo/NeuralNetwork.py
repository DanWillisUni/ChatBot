import random
import numpy as np
from os.path import exists
import matplotlib.pyplot as plt
from datetime import datetime
import time

import PartTwo.Helpers.Fitness as fit
import appSettings

class NeuralNetwork:
    def __init__(self, learningRate):
        self.learningRate = learningRate
        if exists(appSettings.getCurrentSavePath()):
            f = open(appSettings.getCurrentSavePath(), "r")
            content = f.read()
            contList = content.splitlines()
            self.weights = np.array(eval(contList[0].replace("[ ","[").replace(" ]","]")))
            self.bias = np.float(contList[1])
            f.close()
        else:
            self.weights = np.array([np.random.randn(), np.random.randn()])
            self.bias = np.random.randn()
        self.learningRate = learningRate
        self.comparingStations = [None] * 5929

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoidDerivative(self, x):
        return self.sigmoid(x) * (1 - self.sigmoid(x))

    def predict(self, inputVector):
        layerOne = np.dot(inputVector, self.weights) + self.bias #dot product of inputs and weight plus bias
        layerTwo = self.sigmoid(layerOne) # sigmoid layer 1 is the prediction
        prediction = layerTwo
        return prediction

    def calGradients(self, inputVector, target):
        #calculating prediction
        layerOne = np.dot(inputVector, self.weights) + self.bias
        layerTwo = self.sigmoid(layerOne)
        prediction = layerTwo

        diffPredictionTarget = 2 * (prediction - target)
        layerOneDerivative = self.sigmoidDerivative(layerOne)
        layerOneBias = 1
        weights = (0 * self.weights) + (1 * inputVector)

        errorBias = (
            diffPredictionTarget * layerOneDerivative * layerOneBias
        )
        errorWeights = (
                (diffPredictionTarget * layerOneDerivative) * weights
        )

        return errorBias, errorWeights

    def update(self, errorBias, errorWeight):
        self.bias = self.bias - (errorBias * self.learningRate)
        self.weights = self.weights - (
                errorWeight * self.learningRate
        )

    def train(self, inputVectors, targets, iterations):
        meanSquareErrors = []
        for currentIteration in range(iterations):
            # Pick a data instance at random
            randomIndex = random.randint(0, len(inputVectors) - 1)
            inputVector = inputVectors[randomIndex]
            target = targets[randomIndex]
            # Compute the gradients and update the weights
            errorBias, errorWeights = self.calGradients(
                inputVector, target
            )
            self.update(errorBias, errorWeights)
            #printing percentage of training completion
            if (currentIteration % int(iterations/10)) == 0:
                print(str(int(float(currentIteration/iterations) * 100)) + "%")
            if currentIteration % 1000 == 0:
                #print(str(current_iteration) + "/" + str(iterations))
                sumSquaredError = 0.0
                # Loop through all the instances to measure the error
                for dataIndex in range(len(inputVectors)):
                    dataPoint = inputVectors[dataIndex]
                    target = targets[dataIndex]
                    prediction = self.predict(dataPoint)
                    squareError = (prediction - target) ** 2
                    sumSquaredError = sumSquaredError + squareError
                meanSquareErrors.append(sumSquaredError/len(targets))
        with open(appSettings.getCurrentSavePath(), 'w') as f:
            f.write("[{w1},{w2}]\n".format(w1=self.weights[0],w2=self.weights[1]))
            f.write("%s\n" % self.bias)
        return meanSquareErrors

    def startTraining(self,maxDataSize,iterations):
        start = time.time()
        inputs, targets = fit.getNNData(maxDataSize)
        setup = time.time()
        trainingError = self.train(inputs, targets, iterations)  # ~5000 iter per min
        end = time.time()
        print(str(len(targets)) + " datapoints")
        #plotting graph
        plt.plot(trainingError)
        plt.xlabel("Iterations (thousands)")
        plt.ylabel("Mean square error in all training instances")
        now = datetime.now()
        plt.savefig("../resources/PartTwo/NNGraphs/" + now.strftime("%Y%m%d_%H%M%S_") + str(maxDataSize) + ".png")
        plt.close()
        #printing the times
        dlts = time.gmtime(setup - start)
        dl = time.strftime("%H:%M:%S", dlts)
        print("Data load: " + dl)
        ets = time.gmtime(end - start)
        et = time.strftime("%H:%M:%S", ets)
        print("Elapsed: " + et)
    def predictNice(self,delay,nameA,nameB):
        comparingStations,stationDic = fit.getStationCompare()
        input = np.array([delay, int(comparingStations[fit.getStationCompareIndex(stationDic, nameA, nameB)])])
        return self.predict(input)