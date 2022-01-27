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
        Init Neural network object

        Searches for a file with the same layer configuration and loads that if it exists
        Else it randomises weights and bias

        :param layers:
        Array of integers to signal how many nodes are in each layer
        Input layer must have 2 and output must have 1

        """
        self.layer_sizes = layers
        self.params = {}  # set the param dictionary to a new dictionary
        layer_string = ""
        for layer in self.layer_sizes:
            layer_string += "_" + str(layer)  # builds the string of layer sizes
        if exists(appSettings.getNNCurrentSavePath() + layer_string + ".txt"):  # checks if the file with appropriate layers exists
            with open(appSettings.getNNCurrentSavePath() + layer_string + ".txt", "r") as f:  # open the file
                content = f.read()
                cont_split = content.split(";")  # split into the key value pairs
                for kvp in cont_split:
                    if ":" in kvp:  # if it contains a key value pair
                        value_str = (kvp.split(":")[1].replace("\n ", ",").replace(" ", ",")).replace("[,", "[")  # format the value string
                        while ",," in value_str:  # numpy arrays when put into strings can add many spaces so this while loop removes them
                            value_str = value_str.replace(",,", ",")  # replace the double commas with a single
                        arr = np.array(eval(value_str))  # create a numpy array from the string value
                        self.params[kvp.split(":")[0].replace("\n", "")] = arr  # add a new pair to the dictionary
        else:
            for i in range(1, len(self.layer_sizes)):  # for each layer excluding input
                self.params['W' + str(i)] = np.random.randn(self.layer_sizes[i], self.layer_sizes[i - 1]) * 0.01  # initialise weights
                self.params['B' + str(i)] = np.random.randn(self.layer_sizes[i], 1) * 0.01  # initialise biases

    def predict(self, input):
        """      Predicts the delay of a train using the neural network

        :param input:
        Array of data for the 2 input nodes first being the delay to the first station and the second being the normal time between stations

        :return:
        The amount the train will be late to the Second station
        """
        values = self.forward_propagation(input)  # get the values of each layer
        predictions = values['A' + str(len(values) // 2)].T  # get the array that is passed to output
        return predictions  # return the predictions

    def forward_propagation(self, input_vectors):
        """
        Get the values of all the outputs

        :param input_vectors:
        All the inputs for all the data [2,-1]

        :return:
        The value dictionary for all the values of all the nodes on each layer
        """
        layers = len(self.layer_sizes) - 1  # set the number of layers excluding the input
        values = {}  # initialise values dictionary
        for i in range(1, layers + 1):  # for each layer except the input
            if i == 1:  # if it is the first layer after input
                values['Z' + str(i)] = np.dot(self.params['W' + str(i)], input_vectors) + self.params['B' + str(i)]  # use the input to calculate Z
                values['A' + str(i)] = relu(values['Z' + str(i)])  # set the value of the A for the layer to the Relu value of the Z for the layer
            else:
                values['Z' + str(i)] = np.dot(self.params['W' + str(i)], values['A' + str(i - 1)]) + self.params['B' + str(i)]  # use the previous layers A to calculate Z
                if i == layers:  # if its the final layer
                    values['A' + str(i)] = values['Z' + str(i)]  # you don’t apply an activation to the output layer here as we aren’t going to use it to compute any other neuron values
                else:
                    values['A' + str(i)] = relu(values['Z' + str(i)])  # same as the first layer using relu
        return values

    def backward_propagation(self, values, input_vectors, targets):
        """
        Iterate backwards through the layers calculating the gradients

        Here we use the gradients of weights and biases of the next layer to find out the gradients of weights and biases of the previous layer

        :param values:
        Values calculated from forwardPropagation
        :param input_vectors:
        The input data points
        :param targets:
        Array of targets that correspond to the input vectors

        :return:
        The gradients
        """
        layers = len(self.layer_sizes) - 1  # set the number of layers excluding the input
        m = len(targets)  # m is the number of data points
        gradients = {}  # initialise the gradients dictionary to empty
        dz = 0
        for i in range(layers, 0, -1):  # reverse through the layers
            if i == layers:  # if its the end layer
                da = 1 / m * (values['A' + str(i)] - targets)
                dz = da
            else:
                da = np.dot(self.params['W' + str(i + 1)].T, dz)
                dz = np.multiply(da, np.where(values['A' + str(i)] >= 0, 1, 0))
            if i == 1:
                gradients['W' + str(i)] = 1 / m * np.dot(dz, input_vectors.T)
                gradients['B' + str(i)] = 1 / m * np.sum(dz, axis=1, keepdims=True)
            else:
                gradients['W' + str(i)] = 1 / m * np.dot(dz, values['A' + str(i - 1)].T)
                gradients['B' + str(i)] = 1 / m * np.sum(dz, axis=1, keepdims=True)
        return gradients

    def update(self, gradients, learning_rate):
        """
        Update the current weights and values based upon the new gradients calculated

        :param gradients:
        The gradients calculated by the backPropagation
        :param learning_rate:
        The multiplier of the gradient to change the parameters, the smaller number the slower it learns but the easier it is to get a more precise number
        :return:
        Nothing but updates the objects Params dictionary
        """
        layers = len(self.layer_sizes) - 1  # set the number of layers excluding the input
        new_params = {}  # create new dictionary for params
        for i in range(1, layers + 1):  # for each layer
            new_params['W' + str(i)] = self.params['W' + str(i)] - learning_rate * gradients[
                'W' + str(i)]  # set the new weight params to the old params - gradient
            new_params['B' + str(i)] = self.params['B' + str(i)] - learning_rate * gradients[
                'B' + str(i)]  # set the new bias params to the old params - gradient
        self.params = new_params  # update the params

    def save_to_file(self):
        """
        Saves the current params to a text file

        This file name will have the layer configuration in so [2,3,1] will become _2_3_1 to help distinguish configurations
        """
        # get the layer configuration extension
        layers_string = ""
        for layer in self.layer_sizes:
            layers_string += "_" + str(layer)
        with open(appSettings.getNNCurrentSavePath() + layers_string + ".txt", 'w') as f:  # open the file
            for k, v in self.params.items():  # for each key value pair
                f.write(str(k) + ":" + np.array_str(v) + ";\n")  # write key value pair to file split by :

    def train(self, input_vectors, targets, iterations):
        """
        Run the training of the NN

        Prints the percentage finished every 10
        :param input_vectors:
        Array of input data to feed into the forwardPropagation
        :param targets:
        Array of target outcomes which correspond to the inputs
        :param iterations:
        Number of iterations to run for

        :return:
        Root mean squared error value of all the data every 1000 iterations
        """
        root_mean_square_errors = []  # initialise the root mean squared
        for current_iteration in range(iterations):  # for each iteration
            values = self.forward_propagation(input_vectors.T)  # run the forwardPropagation
            gradient = self.backward_propagation(values, input_vectors.T,
                                                 targets.T)  # get the gradients from the backwardsPropagation
            self.update(gradient, 1)  # update the params

            # printing percentage of training completion
            if (current_iteration % int(iterations / 10)) == 0:
                print(str(int(float(current_iteration / iterations) * 100)) + "%")
            if current_iteration % 1000 == 0:  # if the current iteration is divisible by 1000
                sum_squared_error = 0.0
                # Loop through all the instances to measure the error
                for data_index in range(len(input_vectors)):
                    data_point = input_vectors[data_index]  # get the data point
                    target = targets[data_index]  # get the target
                    prediction = self.predict(np.array([[data_point[0]], [data_point[1]]]))[0][0]  # make prediction
                    square_error = (prediction - target) ** 2  # square the difference between the target and the prediction
                    sum_squared_error = sum_squared_error + square_error  # add the squared difference to the sum
                root_mean_square_errors.append(math.sqrt(
                    sum_squared_error / len(targets)))  # add the root mean squared value of all te errors to the array
        self.save_to_file()  # save the new params to a file
        return root_mean_square_errors  # return the array to plot

    def start_training(self, max_data_size, iterations):
        """
        Easy way to initiate training the NN

        :param max_data_size:
        Number of RIDs to expand and process (16000 is used to get all the data)
        :param iterations:
        Number of iterations to train
        :return:
        None but generates a png of the progress of training
        """
        start = time.time()  # start the timer
        inputs, targets = get_nn_data(max_data_size, True)  # get the data removing outliers
        setup = time.time()  # get the setup time point
        training_error = self.train(inputs, targets, iterations)  # train
        end = time.time()  # end the timer
        print(str(len(targets)) + " data points")  # print the number of data points used
        # plot the graph
        for i in range(0, len(training_error), 100):  # this splits the graph up into one hundred thousand iterations per graph
            # plotting graph
            plt.plot(training_error[i:i + 100])
            plt.yscale('linear')
            plt.grid(True)
            plt.xlabel("Iterations (thousands)")
            plt.ylabel("Root Mean square error in all training instances")
            plt.savefig(appSettings.getPathToNNFigures() + datetime.now().strftime("%Y%m%d_%H%M%S_") + str(
                max_data_size) + "_" + str(int((i + 100) / 100)) + ".png")
            plt.close()
        # printing the elapsed times
        dlts = time.gmtime(setup - start)
        dl = time.strftime("%H:%M:%S", dlts)
        print("Data load: " + dl)
        ets = time.gmtime(end - start)
        et = time.strftime("%H:%M:%S", ets)
        print("Elapsed: " + et)
        return training_error

    def predict_nice(self, delay, name_a, name_b):
        """
        Function to be called by the ChatBot having got the station

        :param delay:
        Delay at stationA
        :param name_a:
        Tiploc name of station A
        :param name_b:
        Tiploc name of station B

        :return:
        Prediction in mins as to how late the train is predicted to be
        """
        comparing_stations, station_dic = get_station_compare()  # gets how far the stations are normally
        input = np.array([[delay, int(comparing_stations[get_station_compare_index(station_dic, name_a, name_b)])]])  # format the input to the NN
        return self.predict(input.T)[0][0]  # return the prediction


# These functions are static and do not depend on a NN object but still relevant to the NN
def get_station_compare_index(station_dic, a, b):
    """
    Gets the index of the Stations Compare array to search
    :param station_dic:
    Dictionary of all the stations
    :param a:
    Name of the station A
    :param b:
    Name of the station B
    :return:
    Index of StationCompare Array
    """
    return (station_dic[a] * len(station_dic)) + station_dic[b]  # multiplies the id of the first station by the length of the array (77) then ads the id of the second station


def get_station_compare():
    """
    Gets the station compare array

    If it can find the file it will and read it from there which is way faster
    :return:
    The compare station array which is the average difference in time between planned arrival between all combinations of stations
    Station Dictionary which is all the station names with an ID integer
    """
    all_stations = fit.get_all_stations()  # get all the stations
    station_dic = {}  # initialise blank dictionary as station dictionary
    for i in range(len(all_stations)):  # for all stations
        station_dic[all_stations[i]] = i  # assign each station an id and add it to the dictionary
    if exists(appSettings.getStationComparePath()):  # if the text file exists
        with open(appSettings.getStationComparePath(), "r") as f:  # open the text file
            content = f.read()  # read the file
            comparing_stations = content.splitlines()  # split lines into comparing stations
    else:
        comparing_stations = [None] * 5929  # set comparing stations to empty array
        for a in range(len(all_stations)):  # for each station
            name_a = all_stations[a]  # set the name of station A to the corresponding station in the loop
            for b in range(a + 1, len(all_stations)):  # for each station that hasn't been done
                name_b = all_stations[b]  # set the name of station B to the corresponding station in the loop
                normal_distance = sph.compare_stations(appSettings.get_conn_str(), name_a, name_b)  # get the normal time between station A and B
                if normal_distance != 'None':  # if not Null
                    comparing_stations[get_station_compare_index(station_dic, name_a, name_b)] = int(normal_distance)  # set the index to normal distance
                    comparing_stations[get_station_compare_index(station_dic, name_b, name_a)] = 0 - int(normal_distance)  # set the mirrored index to the negative of the normal distance
        with open(appSettings.getStationComparePath(), 'w') as f:  # open the file
            for item in comparing_stations:  # for each item in the array
                f.write("%s\n" % item)  # write a new item on each line
    return comparing_stations, station_dic


def get_nn_data(max_data_size, remove_outliers):
    """
    Get the data for the NN

    :param max_data_size:
    Number of RIDs to process
    :param remove_outliers:
    Bool stating if the outliers in the data should be removed or not

    :return:
    InputVectors [-1,2]
    Targets array
    """
    conn_str = appSettings.get_conn_str()  # get the connection string
    comparing_stations, station_dic = get_station_compare()  # get the comparing stations and station dictionary
    rids = fit.get_rid_data(max_data_size)  # get the top RIDs
    inputs = np.empty(shape=[0], dtype=int)  # make empty array for the input vectors
    targets = np.empty(shape=[0], dtype=int)  # make an empty array for the targets
    test_for_outliers = []  # make empty array to test for outliers
    for rid in rids:  # for each RID
        rid = rid.replace(" ', ", "")[1:]  # get the rid with no quotes
        rid_data = sph.get_lateness_from_rid(conn_str, rid)  # get all delay times to all the stations from that specific RID
        for a in range(len(rid_data)):  # for all the data on the rid
            name_a = rid_data[a].split(",")[0].replace(" ", "").replace("'", "")  # set the station A name
            delay_a = int(rid_data[a].split(",")[1])  # set the amount that the train was late to station A
            for b in range(a + 1, len(rid_data)):  # for all the data after station A
                name_b = rid_data[b].split(",")[0].replace(" ", "").replace("'", "")  # set the name of station B
                delay_b = int(rid_data[b].split(",")[1])  # set how much the train was late to station B
                input = np.array([delay_a, int(comparing_stations[get_station_compare_index(station_dic, name_a,
                                                                                          name_b)])])  # create the input array for the NN
                inputs = np.append(inputs, input)  # add the input array just created to all the inputs array
                targets = np.append(targets, delay_b)  # add the delay to the second station to the target array
                test_for_outliers.append(abs(delay_a - delay_b))  # add the difference between delay to station A and delay to station B into the array
    if remove_outliers:  # if the outliers are to be removed
        max_allowed_difference = ph.get_outliers_min(test_for_outliers)  # get the max allowed difference before its an outlier
        indexs_to_remove = []
        for i in range(len(targets)):  # for all the indexes
            if abs(inputs[i * 2] - targets[i]) > max_allowed_difference:  # if the difference between delay A and delay B is causes it to be an outlier
                indexs_to_remove.append(i)  # add the index to the index to remove array
        indexs_to_remove.sort()  # sort the indexes
        count = 0
        for index_to_remove in indexs_to_remove:  # for all the indexes
            # print("Removing: " + str(inputs[(indexToRemove - count) * 2]) + " " + str(targets[indexToRemove - count]))
            inputs = np.delete(inputs, (index_to_remove - count) * 2)  # delete the delay for the index
            inputs = np.delete(inputs, ((index_to_remove - count) * 2) + 1)  # delete the normal station time for the index
            targets = np.delete(targets, index_to_remove - count)  # delete the target
            count += 1  # increase the number of removed by 1
    inputs = inputs.reshape((-1, 2))  # reshape the array into the correct dimensions
    return inputs, targets


def train_nn(max_data_size, iterations):
    """
    Friendlier call to start training of the NN

    :param max_data_size:
    Max number of RIDs used in data
    :param iterations:
    Number of iterations to train
    """
    neural_network = get_nn()
    return neural_network.start_training(max_data_size, iterations)


def get_nn():
    """
    Gets the current NN

    :return:
    A NN object being loaded from a file or randomised
    """
    return NeuralNetwork([2, 10, 10, 10, 10, 1])


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
