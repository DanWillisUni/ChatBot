import math
import matplotlib.pyplot as plt
from datetime import datetime

import PartTwo.Helpers.Fitness as fit
import PartTwo.NeuralNetwork as nn
import PartTwo.KNearestNeighbours as knn
import PartTwo.Helpers.SPHelper as sph
import appSettings


def compare_nn_and_knn(iteration_count, data_limit):
    neural_network = nn.get_nn()
    nearest_neighbor = knn.get_knn()
    data, targets = knn.get_knn_data(data_limit, True)
    seknn = 0
    senn = 0
    for i in range(iteration_count):
        data_point, target = fit.sim_result(data, targets)
        knn_r = nearest_neighbor.predict(data_point)
        nn_r = neural_network.predict_nice(data_point[0], data_point[1], data_point[2])
        seknn += (target - knn_r) ** 2
        senn += (target - nn_r) ** 2
        if i % (iteration_count / 10) == 0:
            print(str(int((100 * i) / iteration_count)) + "%")
    print("NN: " + str(math.sqrt(senn / iteration_count)))
    print("KNN: " + str(math.sqrt(seknn / iteration_count)))
    return math.sqrt(senn / iteration_count), math.sqrt(seknn / iteration_count)


def compare_and_train(iteration_count, data_limit, training_iterations, compare_iterations):
    nn_plot = []
    knn_plot = []
    training_error = []
    for i in range(iteration_count):
        nn_accuracy, knn_accuracy = compare_nn_and_knn(compare_iterations, data_limit)
        to_add_training_errors = nn.train_nn(data_limit, training_iterations)
        for ta in to_add_training_errors:
            training_error.append(ta)
        nn_plot.append(nn_accuracy)
        knn_plot.append(knn_accuracy)
        print("COMP: " + str(i) + "/" + str(iteration_count))

    nn_accuracy, knn_accuracy = compare_nn_and_knn(compare_iterations, data_limit)
    nn_plot.append(nn_accuracy)
    knn_plot.append(knn_accuracy)
    # plotting graph
    plt.plot(nn_plot, label="Neural Network")
    plt.plot(knn_plot, label="K Nearest Neighbor")
    plt.yscale('linear')
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.xlabel("Iterations of NN training (100 thousand)")
    plt.ylabel("Root Mean square error of KNN over NN")
    plt.savefig("Comparison" + datetime.now().strftime("_%Y%m%d_%H%M%S") + ".png")
    plt.close()

    plt.plot(training_error)
    plt.yscale('linear')
    plt.grid(True)
    plt.xlabel("Iterations (thousands)")
    plt.ylabel("Root Mean square error in all training instances")
    plt.savefig("FullTrainingData_" + datetime.now().strftime("%Y%m%d_%H%M%S_") + ".png")
    plt.close()

def verify_station_order(from_station, to_station):
    all_stations = fit.get_all_stations()
    if from_station in all_stations:
        if to_station in all_stations:
            normal_distance = sph.compare_stations(appSettings.get_conn_str(),from_station,to_station)
            if normal_distance != 'None':  # if not Null
                if int(normal_distance) > 0:
                    return True
    return False


def predict(from_station, to_station, delay):
   prediction_model = knn.get_knn()
   delay_prediction = prediction_model.predict_nice(delay, from_station, to_station)
   return delay_prediction

# knn.getK(1000,100,1000) # ~12 hours
# compare_and_train(20, 1000, 100000, 1000)  # one hour per iteration
