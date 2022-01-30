import unittest
import datetime
from NLP.nlpu import parse_query
import timedelta


class MyTestCase(unittest.TestCase):
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(hours=24)
    def test_simple_sentence(self):
        query = "What is the cheapest single ticket for four adults and 2 children from Milton Keynes Central to Norwich, arriving at 13:00 on 15/1/2022"
        response = parse_query(query)
        expected = {'query type':   'cheapest',   'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': datetime.datetime(2022, 1, 15, 13, 0), 'type': 'single', 'adult': 4, 'child': 2, 'return_time': None}
        self.assertEqual(expected, response, "test_simple_sentence: Should respond with milton keynes etc")

    def test_leaving_by(self):
        query = "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 on 14/02/20"
        response = parse_query(query)
        expected = { 'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': datetime.datetime(2020, 2, 14, 17, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}
        self.assertEqual(expected, response, "test_leaving_by: Expected London Liv to SWF, leaving by, 17:00 14/02/2022 1 adult")

    def test_today(self):
        query = "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 20:00 today"
        response = parse_query(query)
        expected = {'query type': 'cheapest', 'from': 'London Liverpool Street', 'to': 'South Woodham Ferrers', 'arrive': False, 'time': MyTestCase.today.replace(hour=20, minute=0, second=0, microsecond=0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}
        self.assertEqual(expected, response, "test_today: Expected London Liv to SWF, leaving at 20:00 today")

    def test_tomorrow(self):
        query = "I'd like to book a return ticket from London Euston to Sheffield leaving at 6pm tomorrow"
        response = parse_query(query)
        expected = {'query type': 'cheapest', 'from': 'London Euston', 'to': 'Sheffield', 'arrive': False, 'time': MyTestCase.tomorrow.replace(hour=18, minute=0, second=0, microsecond=0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}
        self.assertEqual(expected, response, "test_tomorrow: Euston to Sheffield tomorrow at 18:00")

    def test_am(self):
        query = "I'd like to book a return ticket from Newcastle to Manchester Piccadilly leaving at 5am on 14th feb"
        response = parse_query(query)
        expected = {'query type': 'cheapest', 'from': 'Newcastle', 'to': 'Manchester Piccadilly', 'arrive': False, 'time': datetime.datetime(2022, 2, 14, 5, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}
        self.assertEqual(expected, response, "test_am: Expected Newcastle to Manchester Piccadilly 5am")

    def test_written_date(self):
        query = "I'd like to book a return ticket from Cambridge to Doncaster leaving at 17:00 on february 14th"
        response = parse_query(query)
        expected = {'query type': 'cheapest', 'from': 'Cambridge', 'to': 'Doncaster', 'arrive': False, 'time': datetime.datetime(2022, 2, 14, 17, 0), 'type': 'return', 'adult': 1, 'child': 0, 'return_time': None}
        self.assertEqual(expected, response, "test_written_date: Expected")

    def test_minute_delay(self):
        query = "What will the delay be at Southampton if the train was delayed 5 minutes from Weymouth?"
        response = parse_query(query)
        expected = {'query type': 'prediction', 'from': 'Weymouth', 'to': 'Southampton', 'delay': 5}
        self.assertEqual(expected, response, "test_minute_delay: Expected 5 min delay Weymouth to Southampton")

    def test_hour_delay(self):
        query = "What will the delay be at Southampton if the train was delayed by 4 hours from Weymouth?"
        response = parse_query(query)
        expected = {'query type': 'prediction', 'from': 'Weymouth', 'to': 'Southampton', 'delay': 240}
        self.assertEqual(expected, response, "test_hour_delay: Expected 240 min delay")

    # this test fails as next week command does not work
    def test_next_week(self):
        next_week_date = MyTestCase.today + datetime.timedelta(days=7)
        query = "What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 next week"
        response = parse_query(query)
        expected ={'query type': 'cheapest', 'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': next_week_date.replace(hour=11, minute=0, second=0, microsecond=0), 'type': 'single', 'adult': 6, 'child': 1, 'return_time': None}
        self.assertEqual(expected, response, "test_next_week: Expacting a date in a weeks time")






"""
    def test_queries(self):

        tests = [
            
            ["What is the predicted delay at Southampton if my train was 3 minutes late from Weymouth?", "{'query type': 'prediction', 'from': 'Weymouth', 'to': 'Southampton', 'delay': 3}"],
            ["What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 on 30/1/2022", "{'query type': 'cheapest', 'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': None, 'type': 'single', 'adult': 6, 'child': 1, 'return_time': None}"],
            ["What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 next week", "{'query type': 'cheapest', 'from': 'Milton Keynes', 'to': 'Norwich', 'arrive': True, 'time': None, 'type': 'single', 'adult': 6, 'child': 1, 'return_time': None}"]
                 ]

        for i in tests :
            attempt = parse_query(i[0])
            self.assertEqual(i[1], attempt.)
"""
if __name__ == '__main__':
    unittest.main()
