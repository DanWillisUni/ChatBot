from collections import Counter
import math
import PartTwo.SPHelper as sph
import appSettings

def knn(data, query, k, d_fn):
    neighbor_distances_and_indices = []
    for index, d in enumerate(data):
        distance = d_fn(d[:-1], query)
        neighbor_distances_and_indices.append((distance, index))# Add the distance and the index of the data to an ordered collection
    sorted_neighbor_distances_and_indices = sorted(neighbor_distances_and_indices)# Sort the ordered collection of distances and indices from smallest to largest (in ascending order) by the distances
    k_nearest_distances_and_indices = sorted_neighbor_distances_and_indices[:k]# Pick the first K entries from the sorted collection
    k_nearest_labels = [data[i][-1] for distance, i in k_nearest_distances_and_indices]#Get the labels of the selected K entries

    return k_nearest_distances_and_indices, mean(k_nearest_labels)

def mean(labels):
    return sum(labels) / len(labels)

def euclidean_distance(point1, point2):
    sum_squared_distance = 0
    for i in range(len(point1)):
        sum_squared_distance += math.pow(point1[i] - point2[i], 2)
    return math.sqrt(sum_squared_distance)

def getKNNRegression(fromStationTPL,toStationTPL,delay):
    connStr = appSettings.getConnStr()
    all = sph.getLatenessOfBoth(connStr, fromStationTPL, toStationTPL)
    if len(all) == 0:
        return delay
    else:
        reg_data = []
        for i in all:
            lineList = []
            lineList.append(int(i.split(",")[0]))
            lineList.append(int(i.split(",")[1]))
            reg_data.append(lineList)
        reg_query = [delay]
        reg_k_nearest_neighbors, reg_prediction = knn(
            reg_data, reg_query, k=5, d_fn=euclidean_distance
        )
        return reg_prediction