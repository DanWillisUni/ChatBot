import math
import matplotlib.pyplot as plt
from datetime import datetime

import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn
import PartTwo.Helpers.SPHelper as sph


def compare_nn_and_knn(iteration_count, data_limit):
    """
    Run the comparison between the neural network and k nearest neighbor

    :param iteration_count:
    Number of iterations to do
    :param data_limit:
    Number of trains data to use

    :return:
    RMSE of the neural network
    RMSE of the k nearest neighbor
    """
    neural_network = nn.get_nn()  # get the neural network obj
    nearest_neighbor = knn.get_knn()  # get the knn obj
    data, targets = knn.get_knn_data(data_limit, True)  # get all the data (removing outliers)
    seknn = 0  # set the sum to 0 for knn
    senn = 0  # set the sum to 0 for nn
    for i in range(iteration_count):  # for the number of iterations
        data_point, target = fit.sim_result(data, targets)  # simulate a result
        knn_r = nearest_neighbor.predict(data_point)  # get the knn result
        nn_r = neural_network.predict_nice(data_point[0], data_point[1], data_point[2])  # get the nn result
        seknn += (target - knn_r) ** 2  # add the squared difference onto the sum
        senn += (target - nn_r) ** 2  # add the squared difference onto the sum
    print("NN: " + str(math.sqrt(senn / iteration_count)))  # print RSME of neural network
    print("KNN: " + str(math.sqrt(seknn / iteration_count)))  # print RMSE of k nearest neighbor
    return math.sqrt(senn / iteration_count), math.sqrt(seknn / iteration_count)  # return


def compare_and_train(iteration_count, data_limit, training_iterations, compare_iterations):
    """
    Compare the neural network and the k nearest neighbor
    Then train the neural network
    Then repeat

    :param iteration_count:
    Number of iterations to do
    :param data_limit:
    Number of trains data to use
    :param training_iterations:
    Number of iterations to train the neural network between each pair
    :param compare_iterations:
    Number of iterations to compare the nn and knn over

    :return:
    Saves PNGs
    """
    nn_plot = []  # initilize array for neural network to plot
    knn_plot = []  # initilize array for knn to plot
    training_error = []  # initilize array for the errors in training of nn
    for i in range(iteration_count):  # for each iteration
        nn_accuracy, knn_accuracy = compare_nn_and_knn(compare_iterations, data_limit)  # compare the nn and knn
        to_add_training_errors = nn.train_nn(data_limit, training_iterations)  # adding training errors to the nn
        for ta in to_add_training_errors:  # for each training error in the errors to add
            training_error.append(ta)  # add the training errors
        nn_plot.append(nn_accuracy)  # add the accuracy to the nn graph
        knn_plot.append(knn_accuracy)  # add the accuracy to the knn graph
        print("COMP: " + str(i) + "/" + str(iteration_count))  # print how far through it is

    nn_accuracy, knn_accuracy = compare_nn_and_knn(compare_iterations, data_limit)  # do one final compare
    nn_plot.append(nn_accuracy)  # add the accuracy to the nn graph
    knn_plot.append(knn_accuracy)  # add the accuracy to the knn graph
    # plotting graphs
    plt.plot(nn_plot, label="Neural Network")  # plotting and labelling NN
    plt.plot(knn_plot, label="K Nearest Neighbor")  # plotting and labeling Knn
    plt.yscale('linear')
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.xlabel("Iterations of NN training (100 thousand)")
    plt.ylabel("Root Mean square error of KNN over NN")
    plt.savefig("Comparison" + datetime.now().strftime("_%Y%m%d_%H%M%S") + ".png")
    plt.close()

    plt.plot(training_error)  # plot all the training errors in the nn
    plt.yscale('linear')
    plt.grid(True)
    plt.xlabel("Iterations (thousands)")
    plt.ylabel("Root Mean square error in all training instances")
    plt.savefig("FullTrainingData_" + datetime.now().strftime("%Y%m%d_%H%M%S_") + ".png")
    plt.close()


def verify_station_order(from_station, to_station):
    """
    :param from_station:
    The station the user wants to do a prediction from
    :param to_station:
    The station the user wants to do a prediction to

    :return:
    False if they are incorrect, True if they are correct
    """
    all_stations = fit.get_all_stations()  # get all the stations in the db
    if from_station in all_stations:  # if the from station is in the list
        if to_station in all_stations:  # if the to station is in the list
            normal_distance = sph.compare_stations(from_station, to_station)  # get the normal time
            if normal_distance != 'None':  # if not Null
                if int(normal_distance) > 0:  # if they are the correct way round
                    return True
    return False


def predict(from_station, to_station, delay):
    """
    Get a prediction from the best model

    :param from_station:
    The station the user wants to do a prediction from
    :param to_station:
    The station the user wants to do a prediction to
    :param delay:
    Delay at the from station

    :return:
    Prediction of how much the user will be late to the to station
    """
    prediction_model = knn.get_knn()  # get the predictive model we are using
    delay_prediction = prediction_model.predict_nice(delay, from_station, to_station)  # do the prediction
    return delay_prediction  # return the prediction



# knn.getK(1000,100,1000) # ~12 hours
# compare_and_train(20, 1000, 100000, 1000)  # one hour per iteration
