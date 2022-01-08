import random
import numpy as np
from os.path import exists
import matplotlib.pyplot as plt
from datetime import datetime
import time

import PartTwo.Helpers.Fitness as fit
import appSettings
import PartTwo.Helpers.SPHelper as sph
import PartTwo.Helpers.ProbabilityHelper as ph

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

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoidDerivative(self, x):
        return self.sigmoid(x) * (1 - self.sigmoid(x))

    def predict(self, inputVector):
        layerOne = np.dot(inputVector, self.weights) + self.bias #dot product of inputs and weight plus bias
        #layerTwo = self.sigmoid(layerOne) # sigmoid layer 1 is the prediction
        prediction = layerOne
        return prediction

    def calGradients(self, inputVector, target):
        #calculating prediction
        layerOne = np.dot(inputVector, self.weights) + self.bias
        #layerTwo = self.sigmoid(layerOne)
        prediction = layerOne

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
        inputs, targets = getNNData(maxDataSize,True)
        setup = time.time()
        trainingError = self.train(inputs, targets, iterations)
        end = time.time()
        print(str(len(targets)) + " datapoints")
        for i in range(0,len(trainingError),100):
            #plotting graph
            plt.plot(trainingError[i:i+100])
            plt.yscale('linear')
            plt.grid(True)
            plt.xlabel("Iterations (thousands)")
            plt.ylabel("Mean square error in all training instances")
            now = datetime.now()
            plt.savefig("../resources/PartTwo/NNGraphs/" + now.strftime("%Y%m%d_%H%M%S_") + str(maxDataSize) + "_" + str(int((i + 100)/100)) +".png")
            plt.close()
        #printing the times
        dlts = time.gmtime(setup - start)
        dl = time.strftime("%H:%M:%S", dlts)
        print("Data load: " + dl)
        ets = time.gmtime(end - start)
        et = time.strftime("%H:%M:%S", ets)
        print("Elapsed: " + et)

    def predictNice(self,delay,nameA,nameB):
        comparingStations,stationDic = getStationCompare()
        input = np.array([delay, int(comparingStations[getStationCompareIndex(stationDic, nameA, nameB)])])
        return self.predict(input)

def getStationCompareIndex(stationDic, A, B):
    return (stationDic[A] * 77) + stationDic[B]

def getStationCompare():
    allStations = fit.getAllStations()
    stationDic = {}
    for i in range(len(allStations)):
        stationDic[allStations[i]] = i

    if exists(appSettings.getStationComparePath()):
        f = open(appSettings.getStationComparePath(), "r")
        content = f.read()
        comparingStations = content.splitlines()
        f.close()
    else:
        comparingStations = [None] * 5929
        for a in range(len(allStations)):
            nameA = allStations[a]
            for b in range(a + 1, len(allStations)):
                nameB = allStations[b]
                normalDistance = sph.compareStations(appSettings.getConnStr(), nameA, nameB)
                if normalDistance != 'None':
                    comparingStations[getStationCompareIndex(stationDic,nameA, nameB)] = int(normalDistance)
                    comparingStations[getStationCompareIndex(stationDic,nameB, nameA)] = 0 - int(normalDistance)
        with open(appSettings.getStationComparePath(), 'w') as f:
            for item in comparingStations:
                f.write("%s\n" % item)
    return comparingStations,stationDic

def getNNData(maxDataSize,removeOutliers):
    connStr = appSettings.getConnStr()
    comparingStations, stationDic = getStationCompare()
    rids = fit.getRidData(maxDataSize)
    inputs = np.empty(shape=[0],dtype=int)
    targets = np.empty(shape=[0],dtype=int)
    testForOutliers = []
    for rid in rids:
        rid = rid.replace(" ', ","")[1:]
        ridData = sph.getLatenessFromRID(connStr,rid)
        for a in range(len(ridData)):
            nameA = ridData[a].split(",")[0].replace(" ","").replace("'","")
            delayA = int(ridData[a].split(",")[1])
            for b in range(a + 1,len(ridData)):
                nameB = ridData[b].split(",")[0].replace(" ","").replace("'","")
                delayB = int(ridData[b].split(",")[1])
                if (removeOutliers and abs(delayB-delayA) < 15) or not removeOutliers:
                    input = np.array([delayA, int(comparingStations[getStationCompareIndex(stationDic,nameA, nameB)])])
                    inputs = np.append(inputs,input)
                    targets = np.append(targets,delayB)
                    testForOutliers.append(abs(delayA - delayB))
    if removeOutliers:
        indexsToRemove = ph.getOutliersIndex(testForOutliers)
        for indexToRemove in indexsToRemove:
            #print("Removing: " + str(inputs[indexToRemove]) + " " + str(targets[indexToRemove]))
            inputs = np.delete(inputs,indexToRemove * 2)
            inputs = np.delete(inputs, (indexToRemove * 2) + 1)
            targets = np.delete(targets,indexToRemove)
    inputs = inputs.reshape((-1,2))
    return inputs,targets

def trainNN(maxDataSize,iterations):
    neuralNetwork = NeuralNetwork(0.1)
    neuralNetwork.startTraining(maxDataSize,iterations)
    return neuralNetwork