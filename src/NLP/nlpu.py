from fuzzywuzzy import process
from datetime import datetime, timedelta
import spacy
from spacy import displacy
import json
import dateparser
import os


nlp = spacy.load('en_core_web_sm')
with open(os.path.join(os.path.dirname(__file__), "stemming/stems.json"), "r") as read_file:
    stems = json.load(read_file)


# load csv of stations
def load_stations():
    data = {}
    csvpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources/stations.csv")
    with open(csvpath) as fp:
        fp.readline()  # throw away first line
        for line in fp:
            fields = line.split(',')
            data[fields[0].lower()] = fields[3].lower()
    return data


#create a map of the loaded stations
station_map = load_stations()


# use fuzzywuzzy to find closest match to inputted stations, high limit as there are lots of matching stations for
# entries such as "london"
def get_matching_stations(station_text):
    return process.extract(station_text, station_map.keys(), limit=50)


# find the station name in the query by looking at the dependencies which are compounds, as these are station names
def extract_station_name(token):
    ntoken = token.doc[token.i + 1]
    name = ntoken.text

    while ntoken.dep_ == 'compound':
        ntoken = ntoken.doc[ntoken.i + 1]
        name += ' ' + ntoken.text
    return name


def extract_journey_time(token):
    # let dateparser allows multiple different date and time formats
    # just keep adding tokens until it fails
    maxtoken = len(token.doc)
    if token.i == maxtoken - 1:
        return None
    ntoken = token.doc[token.i + 1]
    date_str = ntoken.text
    last_tempus = None
    while True:
        tempus = dateparser.parse(date_str)
        if tempus is None and last_tempus is not None:
            return last_tempus
        last_tempus = tempus
        if ntoken.i == maxtoken - 1:
            return last_tempus
        ntoken = ntoken.doc[ntoken.i + 1]
        date_str += ' ' + ntoken.text


# to convert between digits and spelt numbers, using the index
units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one",
        "twenty-two", 'twenty-three', 'twenty-four', 'twenty-five', 'twenty-six',
        'twenty-seven', 'twenty-eight', 'twenty-nine', 'thirty',
        ]


# use units to convert written numbers as an int
def extract_NUM(token):
    ntoken = token.doc[token.i - 1]
    if ntoken.dep_ == 'nummod':
        try:
            return units.index(ntoken.text)
        except ValueError:
            return int(ntoken.text)
    return 1


# if query type is cheapets ticket, this function is used
def cheapest_ticket_query(query):
    doc = nlp(query)
    response = {'query type': 'unknown', 'from': None, 'to': None, 'arrive': False, 'time': datetime.now(), 'type': 'single', 'adult': 1, 'child': 0, 'return_time': None}

    for token in doc:
        # use stems.json to search for a word that indicates cheapest ticket query
        if stems.get("booking_tickets").count(token.lemma_) > 0:
            response["query type"] = "cheapest"
        # search for words in json that indicate the query wants to 'arrive by', if more than one word relates to this,
        # the user wants to arrive by the time they have entered
        elif token.pos_ == 'VERB':
            if stems.get("arrive").count(token.lemma_) > 0 :
                response['arrive'] = True
            # find the time in the query and set this to the outbound time
            response['time'] = extract_journey_time(token)
        # ticket is defaulted to single, so search query for return
        elif token.lemma_.lower() == 'return':
            response['type'] = 'return'
            response['return_time'] = extract_journey_time(token)
        # if adults is mentioned, search for the number associated to adult(s)
        elif token.lemma_ == 'adult':
            response['adult'] = extract_NUM(token)
        # if child(ren) is mentioned, search for the number of associated children
        elif token.lemma_ == 'child':
            response['child'] = extract_NUM(token)
        # find the outbound station
        elif token.pos_ == 'ADP':
            if stems.get("from_station").count(token.lemma_) > 0:
                response['from'] = extract_station_name(token)
            # find the to station
            elif stems.get("to_station").count(token.lemma_) > 0:
                response['to'] = extract_station_name(token)
    return response


# if query type is prediction, this function is used
def prediction_query(query):
    doc = nlp(query)
    response = {'query type': 'unknown', 'from': None, 'to': None, 'delay': None}

    for token in doc:
        # use stems.json to search for a word that indicates it's a prediction query
        if stems.get("prediction").count(token.lemma_) > 0:
            response["query type"] = 'prediction'
        # get the information to do a prediction search such as the stations, and the delay in minutes
        elif token.pos_ == 'ADP':
            if stems.get("from_station").count(token.lemma_) > 0:
                response['from'] = extract_station_name(token)
            elif token.lemma_ == 'at':
                response['to'] = extract_station_name(token)
        elif stems.get("time").count(token.lemma_) > 0:
            if token.lemma_ == "hour":
                time_mins = extract_NUM(token) * 60
                response['delay'] = time_mins
            else:
                response['delay'] = extract_NUM(token)
    return response


# parse the query ready for the scraper
def parse_query(query):
    response = cheapest_ticket_query(query)
    if response['query type'] == 'unknown':
        response = prediction_query(query)
    return response


if __name__ == "__main__":
    '''
    queries = [
        "What is the cheapest single ticket for four adults and 2 children from Milton Keynes Central to Norwich, arriving at 13:00 on 15/1/2022",

        "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 on 14/02/20 for 2 adults and one child",
        "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 today",
        "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 6pm tomorrow",
        "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 5am on 14th feb",
        "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 on february 14th",

        "What will the delay be at Southampton if the train was delayed 5 minutes from Weymouth?",

        "What will the delay be at Southampton if the train was delayed by 4 hours from Weymouth?",

        "What is the predicted delay at Southampton if my train was 3 minutes late from Weymouth?",

        "What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 on 30/1/2022",

        "What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 next week"
    ]
    displacy.serve(nlp(queries[1]), style="dep", port=16000)

    for query in queries:
        response = parse_query(query)
        print(response)

    print(get_matching_stations("london"))
'''
