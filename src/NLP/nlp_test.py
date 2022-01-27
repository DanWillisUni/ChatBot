import unittest
from nlpu import parse_query


class MyTestCase(unittest.TestCase):
    def test_queries(self):

        tests = [
            ["What is the cheapest single ticket for four adults and 2 children from Milton Keynes Central to Norwich, arriving at 13:00 on 15/1/2022", "{'query type': 'cheapest', 'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': datetime.datetime(2022, 1, 15, 13, 0), 'type': 'single', 'adult': 4, 'child': 2, 'return_time': None}"],
            ["I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 on 14/02/20", "{'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': datetime.datetime(2020, 2, 14, 17, 0), 'type': 'return', 'adult': 2, 'child': 1, 'return_time': None}"],
            ["I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 today", "{'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': datetime.datetime(2022, 1, 27, 17, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}"],
            ["I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 6pm tomorrow", "{'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': datetime.datetime(2022, 1, 28, 18, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}"],
            ["I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 5am on 14th feb", "{'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': datetime.datetime(2022, 2, 14, 5, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}"],
            ["I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 on february 14th", "{'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': datetime.datetime(2022, 2, 14, 17, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}"],
            ["What will the delay be at Southampton if the train was delayed 5 minutes from Weymouth?", "{'query type': 'prediction', 'from': 'Weymouth', 'to': 'Southampton', 'delay': 5}"],
            ["What will the delay be at Southampton if the train was delayed by 4 hours from Weymouth?", "{'query type': 'prediction', 'from': 'Weymouth', 'to': 'Southampton', 'delay': 240}"],
            ["What is the predicted delay at Southampton if my train was 3 minutes late from Weymouth?", "{'query type': 'prediction', 'from': 'Weymouth', 'to': 'Southampton', 'delay': 3}"],
            ["What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 on 30/1/2022", "{'query type': 'cheapest', 'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': None, 'type': 'single', 'adult': 6, 'child': 1, 'return_time': None}"],
            ["What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 next week", "{'query type': 'cheapest', 'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': None, 'type': 'single', 'adult': 6, 'child': 1, 'return_time': None}"]
                 ]

        for i in tests :
            attempt = parse_query(i[0])
            self.assertEqual(i[1], attempt.)

if __name__ == '__main__':
    unittest.main()
