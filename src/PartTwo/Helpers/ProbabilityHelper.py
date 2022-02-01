
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


def get_outliers_min(arr):
    """
    Get the minimum number that a value needs to exceed in order to be considered an outlier

    :param arr:
    Input array
    :return:
    Minimum number of an outlier
    """
    q = arr.quartile([0.25, 0.75])  # get the quartiles
    iqr = q[1] - q[0]  # subtract the first from the third to get the interquartile range
    return q[1] + (1.5 * iqr)  # return the third quarter plus 1.5 of the interquartile range
