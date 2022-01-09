import math
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
    '''
    Neural Network class creating the NN obj
    '''
    def __init__(self,layers):
        '''
        Initilises Neural network object

        Searches for a file with the same layer configuration and loads that if it exists
        Else it randomises wieghts and bias

        :param layers:
        Array of integers to signal how many nodes are in each layer
        Input layer must have 2 and output must have 1

        '''
        self.layerSizes = layers
        l = ""
        for layer in self.layerSizes:
            l += "_" + str(layer)#builds the string of layer sizes
        if exists(appSettings.getNNCurrentSavePath() + l + ".txt"):#checks if the file with appropriate layers exists
            self.params = {}#set the param dictionary to a new dictionary
            with open(appSettings.getNNCurrentSavePath() + l + ".txt","r") as f:#open the file
                content = f.read()
                contSplit = content.split(";")#split into the key value pairs
                for KVP in contSplit:
                    if ":" in KVP:#if it contains a key value pair
                        vStr = (KVP.split(":")[1].replace("\n ",",").replace(" ",",")).replace("[,","[")#format the value string
                        while ",," in vStr:#numpty arrays when put into strings can add many spaces so this while loop removes them
                            vStr = vStr.replace(",,",",")#replace the double commas with a single
                        arr = np.array(eval(vStr))#create a numpty array from the string value
                        self.params[KVP.split(":")[0].replace("\n", "")] = arr#add a new pair to the dictionary
        else:
            for i in range(1, len(self.layerSizes)):#for each layer excluding input
                self.params['W' + str(i)] = np.random.randn(self.layerSizes[i], self.layerSizes[i - 1]) * 0.01 #initilise weights
                self.params['B' + str(i)] = np.random.randn(self.layerSizes[i], 1) * 0.01 #initilise biases

    def predict(self, input):
        '''
        Predicts the delay of a train using the neural network

        :param input:
        Array of data for the 2 input nodes

        :return:
        The amount the train will be late to the Second station
        '''
        values = self.forwardPropagation(input)#get the values of each layer
        predictions = values['A' + str(len(values) // 2)].T#get the array that is passed to output
        sum = 0.0
        for i in predictions:#sum the predictions
            sum += i
        return (sum/len(predictions))[0]#return the average of the predictions

    def forwardPropagation(self, inputVectors):
        '''
        Get the values of all the outputs

        :param inputVectors:


        :return:
        '''
        layers = len(self.layerSizes) - 1
        values = {}
        for i in range(1, layers + 1):#for each layer except the input
            if i == 1:
                values['Z' + str(i)] = np.dot(self.params['W' + str(i)], inputVectors) + self.params['B' + str(i)]
                values['A' + str(i)] = relu(values['Z' + str(i)])
            else:
                values['Z' + str(i)] = np.dot(self.params['W' + str(i)], values['A' + str(i - 1)]) + self.params['B' + str(i)]
                if i == layers:
                    values['A' + str(i)] = values['Z' + str(i)]
                else:
                    values['A' + str(i)] = relu(values['Z' + str(i)])
        return values

    def backwardPropagation(self, values, inputVectors, targets):
        layers = len(self.params) // 2
        m = len(targets)
        gradients = {}
        for i in range(layers, 0, -1):
            if i == layers:
                dA = 1 / m * (values['A' + str(i)] - targets)
                dZ = dA
            else:
                dA = np.dot(self.params['W' + str(i + 1)].T, dZ)
                dZ = np.multiply(dA, np.where(values['A' + str(i)] >= 0, 1, 0))
            if i == 1:
                gradients['W' + str(i)] = 1 / m * np.dot(dZ, inputVectors.T)
                gradients['B' + str(i)] = 1 / m * np.sum(dZ, axis=1, keepdims=True)
            else:
                gradients['W' + str(i)] = 1 / m * np.dot(dZ, values['A' + str(i - 1)].T)
                gradients['B' + str(i)] = 1 / m * np.sum(dZ, axis=1, keepdims=True)
        return gradients

    def update(self, grads, learningRate):
        layers = len(self.params) // 2
        newParams = {}
        for i in range(1, layers + 1):
            newParams['W' + str(i)] = self.params['W' + str(i)] - learningRate * grads['W' + str(i)]
            newParams['B' + str(i)] = self.params['B' + str(i)] - learningRate * grads['B' + str(i)]
        self.params = newParams


    def train(self, inputVectors, targets, iterations):
        rootMeanSquareErrors = []
        for currentIteration in range(iterations):
            values = self.forwardPropagation(inputVectors.T)
            grads = self.backwardPropagation(values, inputVectors.T, targets.T)
            self.update(grads, 1)

            #printing percentage of training completion
            if (currentIteration % int(iterations/10)) == 0:
                #print('Cost at iteration ' + str(currentIteration + 1) + ' = ' + str(cost))
                print(str(int(float(currentIteration/iterations) * 100)) + "%")
            if currentIteration % 1000 == 0:
                sumSquaredError = 0.0
                # Loop through all the instances to measure the error
                for dataIndex in range(len(inputVectors)):
                    dataPoint = inputVectors[dataIndex]
                    target = targets[dataIndex]
                    prediction = self.predict(dataPoint)
                    squareError = (prediction - target) ** 2
                    sumSquaredError = sumSquaredError + squareError
                rootMeanSquareErrors.append(math.sqrt(sumSquaredError/len(targets)))
        self.saveToFile()
        return rootMeanSquareErrors

    def saveToFile(self):
        l = ""
        for layer in self.layers:
            l += "_" + str(layer)
        with open(appSettings.getNNCurrentSavePath() + l + ".txt", 'w') as f:
            for k, v in self.params.items():
                f.write(str(k) + ":" + np.array_str(v) + ";\n")

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
            plt.ylabel("Root Mean square error in all training instances")
            plt.savefig(appSettings.getPathToNNFigures() + datetime.now().strftime("%Y%m%d_%H%M%S_") + str(maxDataSize) + "_" + str(int((i + 100)/100)) +".png")
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
    return (stationDic[A] * len(stationDic)) + stationDic[B]

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
    neuralNetwork = getNN()
    neuralNetwork.startTraining(maxDataSize,iterations)
    #return neuralNetwork

def getNN():
    return NeuralNetwork([2, 3, 3, 1])

#ReLU is defined as g(x) = max(0,x). It is 0 when x is negative and equal to x when positive. Due to it’s lower saturation region, it is highly trainable and decreases the cost function far more quickly than sigmoid.
def relu(z):  # takes a numpy array as input and returns activated array
    a = np.maximum(0, z)
    return a