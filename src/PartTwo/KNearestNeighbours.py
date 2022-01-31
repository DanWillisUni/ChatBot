from datetime import datetime
import math
import matplotlib.pyplot as plt

import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.Fitness as fit
import PartTwo.Helpers.ProbabilityHelper as ph


class KNearestNeighbour:
    def __init__(self, k):
        """
        Initilise the KNN object

        :param k:
        The K value for the object
        """
        self.k = k

    def knn(self, data, query):
        """
        Calculates the prediction and the nearest neighbors

        :param data:
        All the data about both stations
        :param query:
        The amount the train is delayed by at the first station
        :return:
        Array of the nearest Neighbors
        Prediction based on the neighbors
        """
        neighbor_distances_and_indices = []  # initilise the array of neighbors
        for index, d in enumerate(data):  # for each in data
            distance = euclidean_distance(d[:-1], query)  # gets the distance between the datas delay and the querys delay
            neighbor_distances_and_indices.append((distance, index))  # Add the distance and the index of the data to an ordered collection
        sorted_neighbor_distances_and_indices = sorted(neighbor_distances_and_indices)  # Sort the ordered collection of distances and indices from smallest to largest (in ascending order) by the distances
        k_nearest_distances_and_indices = sorted_neighbor_distances_and_indices[:self.k]  # Pick the first K entries from the sorted collection
        k_nearest_labels = [data[i][-1] for distance, i in k_nearest_distances_and_indices]  # Get the labels of the selected K entries

        return k_nearest_distances_and_indices, mean(k_nearest_labels)

    def predict(self, datapoint):
        """
        Predict the delay at station B

        :param datapoint:
        Array containing the delay at station A, the name of station A and the name of station B
        :return:
        Prediction of mins late to station B
        """
        return self.predict_nice(datapoint[0], datapoint[1], datapoint[2])  # split the data and use the predictNice function

    def predict_nice(self, delay, from_station_tpl, to_station_tpl):
        """
        Predicts the delay to station B

        This function should be used in the chat bot as it is easier to get the data into

        :param delay:
        The delay at the first station
        :param from_station_tpl:
        The name of the first station
        :param to_station_tpl:
        The name of the second station
        :return:
        The prediction
        """
        all = sph.get_lateness_of_both(from_station_tpl, to_station_tpl)  # get all the data about the two stations
        if len(all) == 0:  # if there is no data
            return delay  # return the delay
        else:
            data = []
            for i in all:#for all the data
                line_list = []
                line_list.append(int(i.split(",")[0]))#add the delay to first to the line array
                line_list.append(int(i.split(",")[1]))#add the delay to second to the line array
                data.append(line_list)#add the line array to the data
            query = [delay]#set the query to the delay
            k_nearest_neighbors, prediction = self.knn(data, query)#call the prediction function
            return prediction


# Static functions KNN specific
def mean(labels):
    """
    Get the mean of the values in the array

    :param labels:
    Array of values
    :return:
    The mean of the values
    """
    return sum(labels) / len(labels)  # get the mean


def euclidean_distance(point1, point2):
    """
    Calculate the eulcidean distance between 2 points

    :param point1:
    First point
    :param point2:
    Second point
    :return:
    The eulcidean distance between the two points
    """
    sum_squared_distance = 0
    for i in range(len(point1)):  # for all the values in the point
        sum_squared_distance += math.pow(point1[i] - point2[i], 2)  # square the difference and add it to the sum
    return math.sqrt(sum_squared_distance)  # square root the sum

def get_knn_data(max_count, remove_outliers):
    """
    Get all the data for the KNN

    :param max_count:
    Number of RIDs to proccess
    :param remove_outliers:
    Bool if the outliers should be removed
    :return:
    All the data for the KNN
    """
    rids = fit.get_rid_data(max_count)  # get all the RIDs inside the maxCount
    input_arr = []
    target_arr = []
    test_for_outliers = []
    for rid in rids:  # for each RID
        rid = rid.replace(" ', ", "")[1:]
        rid_data = sph.get_lateness_from_rid(rid)  # get all the data from the RID
        for a in range(len(rid_data)):  #for all the data in the rid data
            name_a = rid_data[a].split(",")[0].replace(" ", "").replace("'", "")  #get the station name
            delay_a = int(rid_data[a].split(",")[1])  #get the delay at station A
            for b in range(a + 1, len(rid_data)):  #for all the stations after the station A
                name_b = rid_data[b].split(",")[0].replace(" ", "").replace("'", "")  #set the station B name
                delay_b = int(rid_data[b].split(",")[1])  #set the station B delay
                input_arr.append([delay_a, name_a, name_b])  #add data to the input array
                target_arr.append(delay_b)  #add data to the target array
                test_for_outliers.append(abs(delay_a - delay_b))  #add the differnce to the outlier test array
    if remove_outliers:  # if the outliers are to be removed
        max_allowed_difference = ph.get_outliers_min(test_for_outliers)  # get the max allowed difference before its an outlier
        indexs_to_remove = []
        for i in range(len(target_arr)):  # for all the indexes
            if abs(input_arr[i][0] - target_arr[i]) > max_allowed_difference:
                indexs_to_remove.append(i)
        indexs_to_remove.sort()  # sort the indexes
        count = 0
        for indexToRemove in indexs_to_remove:  # for all the indexes
            # print("Removing: " + str(inputArr[indexToRemove - count]) + " " + str(targetArr[indexToRemove - count]))
            del input_arr[indexToRemove - count]  # delete the entry
            del target_arr[indexToRemove - count]  # delete the entry
            count += 1
    return input_arr, target_arr


def get_k(max_data_size, max_k, iterations):
    """
    Test to find the best value of K

    This function doesnt need to be run again but I have left it included

    :param max_data_size:
    Number of RIDs to proccess
    :param max_k:
    Max number to iterate to from 1
    :param iterations:
    Number of iterations to be done

    :return:
    Plots a graph of the data for all the k values
    Writes the results to a csv file
    """
    data, targets = get_knn_data(max_data_size, False)  #get all the data
    se_arr = [0] * max_k  #set up the results array
    for i in range(0, iterations):  #for each iteration
        data_point, target = fit.sim_result(data, targets)  #select a random peice of data and target
        for k in range(1, max_k + 1):  #for each K value
            nearest_neighbor = KNearestNeighbour(k)  #generate a new instance with the k value
            knn_r = nearest_neighbor.predict(data_point)  #predict on the data
            se_arr[k - 1] += (target - knn_r) ** 2  #square the difference between prediction and target and add to sum
        if (i % int(iterations / 10)) == 0:  #if it is a multipule of 10 percent of the way through
            print(str(int(float(i / iterations) * 100)) + "%")  #print the percentage of the way through
    # recording results
    now = datetime.now()#get the time now
    with open(appSettings.getPathToKNNFigures() + "KResults" + now.strftime("_%Y%m%d_%H%M%S") + ".csv", 'w') as f:  # open the file in the write mode
        for k in range(0, max_k):
            se_arr[k] = math.sqrt(se_arr[k] / iterations)  # set the value to the mean squared value
            f.write(str(k + 1) + "," + str(se_arr[k]) + "\n")  # write to the file

    # plotting graph
    plt.plot(se_arr)
    plt.xlabel("K")
    plt.ylabel("Root Mean Squared Errors")
    plt.savefig(appSettings.getPathToKNNFigures() + "searchingForK" + now.strftime("_%Y%m%d_%H%M%S") + ".png")
    plt.close()

def get_knn():
    """
    Gets a new object of the KNN class

    This sets the K value up which was found using the getK function above

    :return:
    A new KNN object
    """
    return KNearestNeighbour(9)  # chose 9 because top is 9 and 8 and 10 are 3rd,4th
