import unittest
import PartTwo.Bayes as b

class MyTestCase(unittest.TestCase):
    def test_Bayes_calculation(self):
        #http://psych.fullerton.edu/mbirnbaum/bayes/bayescalc.html
        toTest = [[0.5,0.4,0.1,0.8],
            [0.1,0.2,0.1,0.18181818181818182],
            [0.9,0.2,0.8,0.6923076923076924],
            [0.4,0.7,0.3,0.6086956521739131],
            [0.1818181,0.6923076,0.6086956,0.20175428971863218]]
        for i in toTest:
            result = b.bayesTheorem(i[0], i[1], i[2])
            self.assertEqual(i[3],result)
    def test_ProbabilityHelper(self):
        self.assertEqual(True,True)



if __name__ == '__main__':
    unittest.main()
