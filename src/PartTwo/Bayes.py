import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.ProbabilityHelper as ph


# calculate P(A|B) given P(A), P(B|A), P(B|not A)
def bayesTheorem(pA, pBGivenA, pBgivenNotA):
    """
	Uses Bayes Theorem to calculate the probability of the train being late

	A is the event of the train being late to the second station
	B is the event of the train being late by delay to the first station

	:param pA:
	Probability of the train being late to second station
	:param pBGivenA:
	Probability of the train being late by delay to the first station given that it turned up late to the second
	:param pBgivenNotA:
	Probability that the train was late by delay to the first station given that it wasnt late to the second
	:return:
	Probability of the train being late to the second station given that it was late to the first station by delay
	"""
    notA = 1 - pA  # calculate P(not A)
    pB = pBGivenA * pA + pBgivenNotA * notA  # calculate P(B)
    pAGivenB = (pBGivenA * pA) / pB  # calculate P(A|B)
    return pAGivenB


def getProbabilityOfLate(delay, fromStationTPL, toStationTPL):
    """
	Calculate the probability of the train being late to the second station

	This uses Bayes Theorem

	:param delay:
	Amount the train was late to the first station in mins
	:param fromStationTPL:
	First station TIPLOC
	:param toStationTPL:
	Second station TIPLOC
	:return:
	Probability of being late to the second station
	"""
    connStr = appSettings.getConnStr()  # get the connection string
    frequencies = sph.getAllDatatOnStation(connStr,
                                           toStationTPL)  # get all the frequenceis of the train lateness to the second station
    pA = ph.probFromFrequency(frequencies, 1)  # get the probability of the train being late to the second station
    frequencies = sph.getLatenessFromStations(connStr, toStationTPL, fromStationTPL, 1,
                                              1500)  # get every time the train was late to the from station
    pBGivenA = ph.probFromFrequency(frequencies,
                                    delay)  # get the probability of the train being late to the first station by delay given that it was late to the second
    frequencies = sph.getLatenessFromStations(connStr, toStationTPL, fromStationTPL, -1500,
                                              0)  # get every time the train was ontime to the from station
    pBGivenNotA = ph.probFromFrequency(frequencies,
                                       delay)  # get the probability of the train being late to the first station by delay given that it was not late to the second
    return bayesTheorem(pA, pBGivenA, pBGivenNotA)  # calcualte the probability
