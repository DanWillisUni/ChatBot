import math
import random
import numpy as np
from os.path import exists

import PartTwo.Helpers.SPHelper as sph
import PartTwo.Helpers.DB as db
import PartTwo.Helpers.Fitness as fit
import appSettings

class NeuralNetwork:
    def __init__(self, learning_rate):
        self.weights = np.array([np.random.randn(), np.random.randn()])
        self.bias = np.random.randn()
        self.learning_rate = learning_rate
        self.stationDic = {}
        self.comparingStations = [None] * 5929

    def _sigmoid(self, x):
        print(x)
        return 1 / (1 + np.exp(-x))

    def _sigmoid_deriv(self, x):
        return self._sigmoid(x) * (1 - self._sigmoid(x))

    def predict(self, input_vector):
        layer_1 = np.dot(input_vector, self.weights) + self.bias
        layer_2 = self._sigmoid(layer_1)
        prediction = layer_2
        return prediction

    def _compute_gradients(self, input_vector, target):
        layer_1 = np.dot(input_vector, self.weights) + self.bias
        layer_2 = self._sigmoid(layer_1)
        prediction = layer_2

        derror_dprediction = 2 * (prediction - target)
        dprediction_dlayer1 = self._sigmoid_deriv(layer_1)
        dlayer1_dbias = 1
        dlayer1_dweights = (0 * self.weights) + (1 * input_vector)

        derror_dbias = (
            derror_dprediction * dprediction_dlayer1 * dlayer1_dbias
        )
        derror_dweights = (
                (derror_dprediction * dprediction_dlayer1) * dlayer1_dweights
        )

        return derror_dbias, derror_dweights

    def _update_parameters(self, derror_dbias, derror_dweights):
        self.bias = self.bias - (derror_dbias * self.learning_rate)
        self.weights = self.weights - (
            derror_dweights * self.learning_rate
        )

    def train(self, input_vectors, targets, iterations):
        cumulative_errors = []
        for current_iteration in range(iterations):
            # Pick a data instance at random
            random_data_index = random.randint(0, len(input_vectors))
            input_vector = input_vectors[random_data_index]
            target = targets[random_data_index]

            # Compute the gradients and update the weights
            derror_dbias, derror_dweights = self._compute_gradients(
                input_vector, target
            )

            self._update_parameters(derror_dbias, derror_dweights)

            # Measure the cumulative error for all the instances
            if current_iteration % 100 == 0:
                cumulative_error = 0
                # Loop through all the instances to measure the error
                for data_instance_index in range(len(input_vectors)):
                    data_point = input_vectors[data_instance_index]
                    target = targets[data_instance_index]

                    prediction = self.predict(data_point)
                    error = np.square(prediction - target)

                    cumulative_error = cumulative_error + error
                cumulative_errors.append(cumulative_error)

        return cumulative_errors

    def getIndex(self,A,B):
        return (self.stationDic[A] * 77) + self.stationDic[B]

    def getStationCompare(self):
        allStations = fit.getAllStations()
        self.stationDic = {}
        for i in range(len(allStations)):
            self.stationDic[allStations[i]] = i

        if exists('comparingStations.txt'):
            f = open('comparingStations.txt', "r")
            content = f.read()
            self.comparingStations = content.splitlines()
            f.close()
        else:
            for a in range(len(allStations)):
                nameA = allStations[a]
                for b in range(a + 1, len(allStations)):
                    nameB = allStations[b]
                    normalDistance = sph.compareStations(appSettings.getConnStr(), nameA, nameB)
                    if normalDistance != 'None':
                        self.comparingStations[self.getIndex(nameA, nameB)] = int(normalDistance)
                        self.comparingStations[self.getIndex(nameB, nameA)] = 0 - int(normalDistance)
            with open('comparingStations.txt', 'w') as f:
                for item in self.comparingStations:
                    f.write("%s\n" % item)

    def getNNData(self):
        connStr = appSettings.getConnStr()
        self.getStationCompare()
        query = 'SELECT distinct rid from nrch_livst_a51'
        rids = db.runQuery(connStr, query)
        rids = rids[:100]
        inputs = np.empty(shape=[0,2],dtype=int)
        targets = np.empty(shape=[0],dtype=int)
        for rid in rids:
            rid = rid.replace(" ', ","")[1:]
            ridData = sph.getLatenessFromRID(connStr,rid)
            for a in range(len(ridData)):
                nameA = ridData[a].split(",")[0].replace(" ","").replace("'","")
                delayA = int(ridData[a].split(",")[1])
                for b in range(a + 1,len(ridData)):
                    nameB = ridData[b].split(",")[0].replace(" ","").replace("'","")
                    delayB = int(ridData[b].split(",")[1])
                    input = np.array([delayA, int(self.comparingStations[self.getIndex(nameA,nameB)])])
                    inputs = np.vstack((inputs,input))
                    targets = np.append(targets,delayB)
        return inputs,targets