import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.ProbabilityHelper as ph


# calculate P(A|B) given P(A), P(B|A), P(B|not A)
def bayes_theorem(p_a, p_b_given_a, p_b_given_not_a):
    """
    Uses Bayes Theorem to calculate the probability of the train being late

    A is the event of the train being late to the second station
    B is the event of the train being late by delay to the first station

    :param p_a:
    Probability of the train being late to second station
    :param p_b_given_a:
    Probability of the train being late by delay to the first station given that it turned up late to the second
    :param p_b_given_not_a:
    Probability that the train was late by delay to the first station given that it wasnt late to the second
    :return:
    Probability of the train being late to the second station given that it was late to the first station by delay
    """
    not_a = 1 - p_a  # calculate P(not A)
    p_b = p_b_given_a * p_a + p_b_given_not_a * not_a  # calculate P(B)
    p_a_given_b = (p_b_given_a * p_a) / p_b # calculate P(A|B)
    return p_a_given_b


def getProbabilityOfLate(delay, from_station_tpl, to_station_tpl):
    """
    Calculate the probability of the train being late to the second station

    This uses Bayes Theorem

    :param delay:
    Amount the train was late to the first station in mins
    :param from_station_tpl:
    First station TIPLOC
    :param to_station_tpl:
    Second station TIPLOC
    :return:
    Probability of being late to the second station
    """
    conn_str = appSettings.get_conn_str()  # get the connection string
    frequencies = sph.get_all_data_on_station(conn_str, to_station_tpl)  # get all the frequenceis of the train lateness to the second station
    p_a = ph.probability_from_frequency(frequencies, 1)  # get the probability of the train being late to the second station
    frequencies = sph.get_lateness_from_stations(conn_str, to_station_tpl, from_station_tpl, 1, 1500)  # get every time the train was late to the to station
    p_b_given_a = ph.probability_from_frequency(frequencies, delay)  # get the probability of the train being late to the first station by delay given that it was late to the second
    frequencies = sph.get_lateness_from_stations(conn_str, to_station_tpl, from_station_tpl, -1500, 0)  # get every time the train was ontime to the to station
    p_b_given_not_a = ph.probability_from_frequency(frequencies, delay)  # get the probability of the train being late to the first station by delay given that it was not late to the second
    return bayes_theorem(p_a, p_b_given_a, p_b_given_not_a)  # calcualte the probability
