import PartTwo.Helpers.SPHelper as sph
import appSettings
import PartTwo.Helpers.ProbabilityHelper as ph

# calculate P(A|B) given P(A), P(B|A), P(B|not A)
def bayes_theorem(p_a, p_b_given_a, p_b_given_not_a):
	not_a = 1 - p_a # calculate P(not A)
	p_b = p_b_given_a * p_a + p_b_given_not_a * not_a # calculate P(B)
	p_a_given_b = (p_b_given_a * p_a) / p_b# calculate P(A|B)
	return p_a_given_b

def getProbabilityOfLate(fromStationTPL,toStationTPL,delay):
	connStr = appSettings.getConnStr()
	frequencies = sph.getAllDatatOnStation(connStr, toStationTPL)
	p_a = ph.probFromFrequency(frequencies,1)
	frequencies = sph.getLatenessFromStations(connStr, toStationTPL, fromStationTPL, 1, 1500)#it is suppsed to be that way around, trust me
	p_b_given_a = ph.probFromFrequency(frequencies,delay)
	frequencies = sph.getLatenessFromStations(connStr, toStationTPL, fromStationTPL, -1500, 0)
	p_b_given_not_a = ph.probFromFrequency(frequencies,delay)
	return bayes_theorem(p_a,p_b_given_a,p_b_given_not_a)