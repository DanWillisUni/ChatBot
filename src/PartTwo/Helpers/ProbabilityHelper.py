import math


def probability_from_frequency(f, min):
    """
    Get the probability that the result is over the min from the frequency array

    :param f:
    Frequency array
    :param min:
    Minimum value to count to the probability
    :return:
    Probability that if a random value is picked it is over the minimum value
    """
    total_frequency = 0
    total_late = 0
    for i in f:  # for each frequency
        total_frequency += int((i.split(",")[1]))  # add the frequency to the total frequency
        if int((i.split(",")[0])) >= min:  # if the value is greater than or equal to the minimum
            total_late += int((i.split(",")[1]))  # add the frequency to the late total
    return float(total_late / total_frequency)  # divide the total late by the total


def get_q(arr, q_multiplyer):
    """
    Get quarters for interquartilerange

    :param arr:
    Input array of values
    :param q_multiplyer:
    To multiply the length of the array by
    (0.25 for first quarter, 0.5 for median and 0.75 for 3rd quarter)

    :return:
    The array value that is at the index of the multiplyer times the length when it is sorted
    """
    arr.sort()  # sort the array
    array_length = len(arr)  # get the length of the array
    index = array_length * q_multiplyer  # set the index to the correct place
    if index % 1 == 0:  # if the index is an integer
        return arr[int(index)]  # return the array value at the index
    elif index % 1 == 0.5:  # else if the index ends in .5
        return (arr[math.floor(index)] + arr[math.ceil(index)])/2  # average the two numbers the index is between
    else:
        return arr[round(index)]  # round the index to the nearest integer


def get_outliers_min(arr):
    """
    Get the minimum number that a value needs to exceed in order to be considered an outlier

    :param arr:
    Input array
    :return:
    Minimum number of an outlier
    """
    q1 = get_q(arr, 0.25)  # get the first quarter
    q3 = get_q(arr, 0.75)  # get the third quarter
    iqr = q3 - q1  # subtract the first from the third to get the interquartile range
    return q3 + (1.5 * iqr)  # return the third quarter plus 1.5 of the interquartile range
