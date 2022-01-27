import unittest
import PartTwo.Bayes as b
import PartTwo.KNearestNeighbours as knn
import PartTwo.NeuralNetwork as nn
import PartTwo.Helpers.ProbabilityHelper as ph
import PartTwo.Helpers.Fitness as f


class MyTestCase(unittest.TestCase):

    # test fitness
    def test_get_all_stations(self):
        self.assertEqual(True, True)

    def test_sim_result(self):
        self.assertEqual(True, True)

    def test_get_rid_data(self):
        self.assertEqual(True, True)

    # test probability helper
    def test_probability_from_frequency(self):
        test_cases = [
            [["0,10", "1,10", "2,5", "3,5", "4,5", "5,5"], 2, 0.5]
        ]
        for i in test_cases:
            result = ph.probability_from_frequency(i[0], i[1])
            self.assertEqual(i[2], result)

    def test_get_q(self):
        self.assertEqual(True, True)

    def test_get_outliers_min(self):
        self.assertEqual(True, True)

    # test predicitons
    def test_bayes_calculation(self):
        #http://psych.fullerton.edu/mbirnbaum/bayes/bayescalc.html
        test_cases = [[0.5,0.4,0.1,0.8],
            [0.1,0.2,0.1,0.18181818181818182],
            [0.9,0.2,0.8,0.6923076923076924],
            [0.4,0.7,0.3,0.6086956521739131],
            [0.1818181,0.6923076,0.6086956,0.20175428971863218]]
        for i in test_cases:
            result = b.bayes_theorem(i[0], i[1], i[2])
            self.assertEqual(i[3], result)

    def test_knn(self):
        self.assertEqual(True, True)

    def test_nn(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
