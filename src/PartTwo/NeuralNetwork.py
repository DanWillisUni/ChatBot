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
    """
    Neural Network class creating the NN obj
    """

    def __init__(self, layers):
        """
        Initilises Neural network object

        Searches for a file with the same layer configuration and loads that if it exists
        Else it randomises wieghts and bias

        :param layers:
        Array of integers to signal how many nodes are in each layer
        Input layer must have 2 and output must have 1

        """
        self.layerSizes = layers
        self.params = {}  # set the param dictionary to a new dictionary
        l = ""
        for layer in self.layerSizes:
            l += "_" + str(layer)  # builds the string of layer sizes
        if exists(appSettings.getNNCurrentSavePath() + l + ".txt"):  # checks if the file with appropriate layers exists

            with open(appSettings.getNNCurrentSavePath() + l + ".txt", "r") as f:  # open the file
                content = f.read()
                contSplit = content.split(";")  # split into the key value pairs
                for KVP in contSplit:
                    if ":" in KVP:  # if it contains a key value pair
                        vStr = (KVP.split(":")[1].replace("\n ", ",").replace(" ", ",")).replace("[,",
                                                                                                 "[")  # format the value string
                        while ",," in vStr:  # numpty arrays when put into strings can add many spaces so this while loop removes them
                            vStr = vStr.replace(",,", ",")  # replace the double commas with a single
                        arr = np.array(eval(vStr))  # create a numpty array from the string value
                        self.params[KVP.split(":")[0].replace("\n", "")] = arr  # add a new pair to the dictionary
        else:
            for i in range(1, len(self.layerSizes)):  # for each layer excluding input
                self.params['W' + str(i)] = np.random.randn(self.layerSizes[i],
                                                            self.layerSizes[i - 1]) * 0.01  # initilise weights
                self.params['B' + str(i)] = np.random.randn(self.layerSizes[i], 1) * 0.01  # initilise biases

    def predict(self, input):
        """      Predicts the delay of a train using the neural network

        :param input:
        Array of data for the 2 input nodes first being the delay to the first station and the second being the normal time between stations

        :return:
        The amount the train will be late to the Second station
        """
        values = self.forwardPropagation(input)  # get the values of each layer
        predictions = values['A' + str(len(values) // 2)].T  # get the array that is passed to output
        return predictions  # return the predictions

    def forwardPropagation(self, inputVectors):
        """
        Get the values of all the outputs

        :param inputVectors:
        All the inputs for all the data [2,-1]

        :return:
        The value dictionary for all the values of all the nodes on each layer
        """
        layers = len(self.layerSizes) - 1  # set the number of layers excluding the input
        values = {}  # initilise values dictionary
        for i in range(1, layers + 1):  # for each layer except the input
            if i == 1:  # if it is the first layer after input
                values['Z' + str(i)] = np.dot(self.params['W' + str(i)], inputVectors) + self.params[
                    'B' + str(i)]  # use the input to calculate Z
                values['A' + str(i)] = relu(values['Z' + str(
                    i)])  # set the value of the A for the layer to the Relu value of the Z for the layer
            else:
                values['Z' + str(i)] = np.dot(self.params['W' + str(i)], values['A' + str(i - 1)]) + self.params[
                    'B' + str(i)]  # use the previuos layers A to calculate Z
                if i == layers:  # if its the final layer
                    values['A' + str(i)] = values['Z' + str(
                        i)]  # you don’t apply an activation to the output layer here as we aren’t going to use it to compute any other neuron values
                else:
                    values['A' + str(i)] = relu(values['Z' + str(i)])  # same as the first layer using relu
        return values

    def backwardPropagation(self, values, inputVectors, targets):
        """
        Iterate backwards through the layers calculating the gradients

        Here we use the gradients of weights and biases of the next layer to find out the gradients of weights and biases of the previous layer

        :param values:
        Values calculated from forwardPropagation
        :param inputVectors:
        The input datapoints
        :param targets:
        Array of targets that correspond to the input vectors

        :return:
        The gradients
        """
        layers = len(self.layerSizes) - 1  # set the number of layers excluding the input
        m = len(targets)  # m is the number of datapoints
        gradients = {}  # initilise the gradients dictionary to empty
        for i in range(layers, 0, -1):  # reverse through the layers
            if i == layers:  # if its the end layer
                deltaA = 1 / m * (values['A' + str(i)] - targets)
                deltaZ = deltaA
            else:
                deltaA = np.dot(self.params['W' + str(i + 1)].T, deltaZ)
                deltaZ = np.multiply(deltaA, np.where(values['A' + str(i)] >= 0, 1, 0))
            if i == 1:
                gradients['W' + str(i)] = 1 / m * np.dot(deltaZ, inputVectors.T)
                gradients['B' + str(i)] = 1 / m * np.sum(deltaZ, axis=1, keepdims=True)
            else:
                gradients['W' + str(i)] = 1 / m * np.dot(deltaZ, values['A' + str(i - 1)].T)
                gradients['B' + str(i)] = 1 / m * np.sum(deltaZ, axis=1, keepdims=True)
        return gradients

    def update(self, gradients, learningRate):
        """
        Update the current weights and values based upon the new gradients calculated

        :param gradients:
        The gradients calculated by the backPropagation
        :param learningRate:
        The multiplyer of the gradient to change the parameters, the smaller number the slower it learns but the easier it is to get a more precise number
        :return:
        Nothing but updates the objects Params dictionary
        """
        layers = len(self.layerSizes) - 1  # set the number of layers excluding the input
        newParams = {}  # create new dictionary for params
        for i in range(1, layers + 1):  # for each layer
            newParams['W' + str(i)] = self.params['W' + str(i)] - learningRate * gradients[
                'W' + str(i)]  # set the new weight params to the old params - gradient
            newParams['B' + str(i)] = self.params['B' + str(i)] - learningRate * gradients[
                'B' + str(i)]  # set the new bias params to the old params - gradient
        self.params = newParams  # update the params

    def saveToFile(self):
        """
        Saves the current params to a text file

        This file name will have the layer configuration in so [2,3,1] will become _2_3_1 to help distinguish configurations
        """
        # get the layer configuration extension
        l = ""
        for layer in self.layerSizes:
            l += "_" + str(layer)
        with open(appSettings.getNNCurrentSavePath() + l + ".txt", 'w') as f:  # open the file
            for k, v in self.params.items():  # for each key value pair
                f.write(str(k) + ":" + np.array_str(v) + ";\n")  # write key value pair to file seperated by :

    def train(self, inputVectors, targets, iterations):
        """
        Run the training of the NN

        Prints the percentage finished every 10
        :param inputVectors:
        Array of input data to feed into the forwardPropagation
        :param targets:
        Array of target outcomes which correspond to the inputs
        :param iterations:
        Number of iterations to run for

        :return:
        Root mean squared error value of all the data every 1000 iterations
        """
        rootMeanSquareErrors = []  # initilise the root mean squared
        for currentIteration in range(iterations):  # for each iteration
            values = self.forwardPropagation(inputVectors.T)  # run the forwardPropagation
            gradient = self.backwardPropagation(values, inputVectors.T,
                                                targets.T)  # get the gradients from the backwardsPropagation
            self.update(gradient, 1)  # update the params

            # printing percentage of training completion
            if (currentIteration % int(iterations / 10)) == 0:
                print(str(int(float(currentIteration / iterations) * 100)) + "%")
            if currentIteration % 1000 == 0:  # if the current iteration is divisable by 1000
                sumSquaredError = 0.0
                # Loop through all the instances to measure the error
                for dataIndex in range(len(inputVectors)):
                    dataPoint = inputVectors[dataIndex]  # get the data point
                    target = targets[dataIndex]  # get the target
                    prediction = self.predict(np.array([[dataPoint[0]], [dataPoint[1]]]))[0][0]  # make prediction
                    squareError = (
                                              prediction - target) ** 2  # square the difference between the target and the prediction
                    sumSquaredError = sumSquaredError + squareError  # add the squared difference to the sum
                rootMeanSquareErrors.append(math.sqrt(
                    sumSquaredError / len(targets)))  # add the root mean squared value of all te errors to the array
        self.saveToFile()  # save the new params to a file
        return rootMeanSquareErrors  # return the array to plot

    def startTraining(self, maxDataSize, iterations):
        """
        Easy way to initiate training the NN

        :param maxDataSize:
        Number of RIDs to expand and process (16000 is used to get all the data)
        :param iterations:
        Number of iterations to train
        :return:
        None but generates a png of the progress of training
        """
        start = time.time()  # start the timer
        inputs, targets = getNNData(maxDataSize, True)  # get the data removing outliers
        setup = time.time()  # get the setup time point
        trainingError = self.train(inputs, targets, iterations)  # train
        end = time.time()  # end the timer
        print(str(len(targets)) + " datapoints")  # print the number of data points used
        # plot the graph
        for i in range(0, len(trainingError),
                       100):  # this splits the graph up into one hundred thousand iterations per graph
            # plotting graph
            plt.plot(trainingError[i:i + 100])
            plt.yscale('linear')
            plt.grid(True)
            plt.xlabel("Iterations (thousands)")
            plt.ylabel("Root Mean square error in all training instances")
            plt.savefig(appSettings.getPathToNNFigures() + datetime.now().strftime("%Y%m%d_%H%M%S_") + str(
                maxDataSize) + "_" + str(int((i + 100) / 100)) + ".png")
            plt.close()
        # printing the elapsed times
        dlts = time.gmtime(setup - start)
        dl = time.strftime("%H:%M:%S", dlts)
        print("Data load: " + dl)
        ets = time.gmtime(end - start)
        et = time.strftime("%H:%M:%S", ets)
        print("Elapsed: " + et)

    def predictNice(self, delay, nameA, nameB):
        """
        Function to be called by the ChatBot having got the station

        :param delay:
        Delay at stationA
        :param nameA:
        Tiploc name of station A
        :param nameB:
        Tiploc name of station B

        :return:
        Prediction in mins as to how late the train is predicted to be
        """
        comparingStations, stationDic = getStationCompare()  # gets how far the stations are normally
        input = np.array([[delay, int(
            comparingStations[getStationCompareIndex(stationDic, nameA, nameB)])]])  # format the input to the NN
        return self.predict(input.T)[0][0]  # return the prediction


# These fuctions are static and do not depend on a NN object but still relivent to the NN
def getStationCompareIndex(stationDic, A, B):
    """
    Gets the index of the Stations Compare array to search
    :param stationDic:
    Dictionary of all the stations
    :param A:
    Name of the station A
    :param B:
    Name of the station B
    :return:
    Index of StationCompare Array
    """
    return (stationDic[A] * len(stationDic)) + stationDic[
        B]  # multiplys the id of the first station by the length of the array (77) then ads the id of the second station


def getStationCompare():
    """
    Gets the station compare array

    If it can find the file it will and read it from there which is way faster
    :return:
    The compare station array which is the average difference in time between planned arrival between all combinations of stations
    Station Dictionary which is all the station names with an ID integer
    """
    allStations = fit.getAllStations()  # get all the stations
    stationDic = {}  # initilise blank dictionary as station dictionary
    for i in range(len(allStations)):  # for all stations
        stationDic[allStations[i]] = i  # assign each station an id and add it to the dictionary

    if exists(appSettings.getStationComparePath()):  # if the textfile exists
        with open(appSettings.getStationComparePath(), "r") as f:  # open the text file
            content = f.read()  # read the file
            comparingStations = content.splitlines()  # split lines into comparing stations
    else:
        comparingStations = [None] * 5929  # set comparing stations to empty array
        for a in range(len(allStations)):  # for each station
            nameA = allStations[a]  # set the name of station A to the corresponding station in the loop
            for b in range(a + 1, len(allStations)):  # for each station that hasnt been done
                nameB = allStations[b]  # set the name of station B to the corresponding station in the loop
                normalDistance = sph.compareStations(appSettings.getConnStr(), nameA,
                                                     nameB)  # get the normal time between station A and B
                if normalDistance != 'None':  # if not Null
                    comparingStations[getStationCompareIndex(stationDic, nameA, nameB)] = int(
                        normalDistance)  # set the index to normal distance
                    comparingStations[getStationCompareIndex(stationDic, nameB, nameA)] = 0 - int(
                        normalDistance)  # set the mirrored index to the negative of the normal distance
        with open(appSettings.getStationComparePath(), 'w') as f:  # open the file
            for item in comparingStations:  # for each item in the array
                f.write("%s\n" % item)  # write a new item on each line
    return comparingStations, stationDic


def getNNData(maxDataSize, removeOutliers):
    """
    Get the data for the NN

    :param maxDataSize:
    Number of RIDs to proccess
    :param removeOutliers:
    Bool stating if the outliers in the data should be removed or not

    :return:
    InputVectors [-1,2]
    Targets array
    """
    connStr = appSettings.getConnStr()  # get the connection string
    comparingStations, stationDic = getStationCompare()  # get the comparing stations and station dictionary
    rids = fit.getRidData(maxDataSize)  # get the top RIDs
    inputs = np.empty(shape=[0], dtype=int)  # make empty array for the input vectors
    targets = np.empty(shape=[0], dtype=int)  # make an empty array for the targets
    testForOutliers = []  # make empty array to test for outliers
    for rid in rids:  # for each RID
        rid = rid.replace(" ', ", "")[1:]  # get the rid with no quotes
        ridData = sph.getLatenessFromRID(connStr, rid)  # get all delay times to all the stations from that specific RID
        for a in range(len(ridData)):  # for all the data on the rid
            nameA = ridData[a].split(",")[0].replace(" ", "").replace("'", "")  # set the station A name
            delayA = int(ridData[a].split(",")[1])  # set the amount that the train was late to station A
            for b in range(a + 1, len(ridData)):  # for all the data after station A
                nameB = ridData[b].split(",")[0].replace(" ", "").replace("'", "")  # set the name of station B
                delayB = int(ridData[b].split(",")[1])  # set how much the train was late to station B
                input = np.array([delayA, int(comparingStations[getStationCompareIndex(stationDic, nameA,
                                                                                       nameB)])])  # create the input array for the NN
                inputs = np.append(inputs, input)  # add the input array just created to all the inputs array
                targets = np.append(targets, delayB)  # add the delay to the second station to the target array
                testForOutliers.append(
                    abs(delayA - delayB))  # add the difference between delay to station A and delay to station B into the array
    if removeOutliers:  # if the outliers are to be removed
        maxAllowedDifference = ph.getOutliersMin(
            testForOutliers)  # get the max allowed difference before its an outlier
        indexsToRemove = []
        for i in range(len(targets)):  # for all the indexes
            if abs(inputs[i * 2] - targets[
                i]) > maxAllowedDifference:  # if the difference between delay A and delay B is causes it to be an outlier
                indexsToRemove.append(i)  # add the index to the index to remove array
        indexsToRemove.sort()  # sort the indexes
        count = 0
        for indexToRemove in indexsToRemove:  # for all the indexes
            # print("Removing: " + str(inputs[(indexToRemove - count) * 2]) + " " + str(targets[indexToRemove - count]))
            inputs = np.delete(inputs, (indexToRemove - count) * 2)  # delete the delay for the index
            inputs = np.delete(inputs,
                               ((indexToRemove - count) * 2) + 1)  # delete the normal station time for the index
            targets = np.delete(targets, indexToRemove - count)  # delete the target
            count += 1  # increase the number of removed by 1
    inputs = inputs.reshape((-1, 2))  # reshape the array into the correct dimensions
    return inputs, targets


def trainNN(maxDataSize, iterations):
    """
    Friendlier call to start training of the NN

    :param maxDataSize:
    Max number of RIDs used in data
    :param iterations:
    Number of iterations to train
    """
    neuralNetwork = getNN()
    neuralNetwork.startTraining(maxDataSize, iterations)
    # return neuralNetwork


def getNN():
    """
    Gets the current NN

    :return:
    A NN object being loaded from a file or randomised
    """
    return NeuralNetwork([2, 3, 3, 1])


def relu(z):
    """
    Activated the array

    ReLU is defined as g(x) = max(0,x). It is 0 when x is negative and equal to x when positive. Due to it’s lower saturation region, it is highly trainable and decreases the cost function far more quickly than sigmoid.

    :param z:
    a numpy array
    :return:
    activated array
    """
    a = np.maximum(0, z)
    return a
