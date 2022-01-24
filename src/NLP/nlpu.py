from fuzzywuzzy import process
from datetime import datetime, timedelta
import spacy
from spacy import displacy
import json
from os.path import dirname
import pandas as pd

project_root = dirname(dirname(__file__))

nlp = spacy.load('en_core_web_sm')
with open(project_root + "/NLP/stemming/stems.json", "r") as read_file:
    stems = json.load(read_file)


def load_stations():
    data = {}
    with open('../../resources/stations.csv') as fp:
        fp.readline()  # throw away first line
        for line in fp:
            fields = line.split(',')
            data[fields[0].lower()] = fields[3].lower()
    return data


station_map = load_stations()

# use fuzzywuzzy to find closest match to inputted station
def get_matching_stations(station_text):
    return process.extract(station_text, station_map.keys(), limit=50)


def extract_station_name(token):
    ntoken = token.doc[token.i + 1]
    name = ntoken.text

    while ntoken.dep_ == 'compound':
        ntoken = ntoken.doc[ntoken.i + 1]
        name += ' ' + ntoken.text
    return name


def extract_journey_time(token):
    try:
        # expecting VERB (by)? NUM (on)? NUM
        ntoken = token.doc[token.i + 1]
        if ntoken.dep_ == 'prep':
            ntoken = token.doc[ntoken.i + 1]

        time_str = ntoken.text

        ntoken = token.doc[ntoken.i + 1]
        if ntoken.dep_ == 'prep':
            ntoken = token.doc[ntoken.i + 1]

        try:
            tempus = datetime.strptime(f'{time_str} {ntoken.text}', '%H:%M %d/%m/%Y')
        except ValueError:
            try:
                tempus = datetime.strptime(f'{time_str} {ntoken.text}', '%H:%M %d/%m/%y')
            except ValueError:
                tempus = None

        return tempus
    except IndexError:  # Wrapping this method because single word inputs will break it
        return None


units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one",
        "twenty-two", 'twenty-three', 'twenty-four', 'twenty-five', 'twenty-six',
        'twenty-seven', 'twenty-eight', 'twenty-nine', 'thirty',
        ]


def extract_NUM(token):
    try:
        ntoken = token.doc[token.i - 1]
        if ntoken.dep_ == 'nummod':
            try:
                return units.index(ntoken.text)
            except ValueError:
                return int(ntoken.text)
        return 1
    except IndexError:
        return 1


def cheapest_ticket_query(query):
    doc = nlp(query)
    response = {'query type': 'unknown', 'from': None, 'to': None, 'arrive': False, 'time': pd.Timestamp(datetime.now()).ceil("15min").to_pydatetime(), 'type': 'single', 'adult': 1, 'child': 0, 'return_time': None}

    for token in doc:
        if stems.get("booking_tickets").count(token.lemma_) > 0:
            response["query type"] = "cheapest"
        elif token.pos_ == 'VERB':
            if stems.get("arrive").count(token.lemma_) > 0 :
                response['arrive'] = True
            response['time'] = extract_journey_time(token)
        elif token.lemma_.lower() == 'return':
            response['type'] = 'return'
            response['return_time'] = extract_journey_time(token)
        elif token.lemma_ == 'adult':
            response['adult'] = extract_NUM(token)
        elif token.lemma_ == 'child':
            response['child'] = extract_NUM(token)
        elif token.pos_ == 'ADP':
            if stems.get("from_station").count(token.lemma_) > 0:
                response['from'] = extract_station_name(token)
            elif stems.get("to_station").count(token.lemma_) > 0:
                response['to'] = extract_station_name(token)
    return response


def prediction_query(query):
    doc = nlp(query)
    response = {'query type': 'unknown', 'from': None, 'to': None, 'delay': None}

    for token in doc:
        if stems.get("prediction").count(token.lemma_) > 0:
            response["query type"] = 'prediction'
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


def parse_query(query):
    response = cheapest_ticket_query(query)
    if response['query type'] == 'unknown':
        response = prediction_query(query)
    return response


if __name__ == "__main__":
    queries = [
        "What is the cheapest single ticket for four adults and 2 children from Milton Keynes Central to Norwich, arriving at 13:00 on 15/2/2022",  # TODO: Can't recognise MKC, and I updated the time to be in the future
        
        "I'd like to book a return ticket from London Liverpool Street to South Woodham Ferrers leaving at 17:00 on 14/02/22",  # TODO: London Liverpool Street is actually Liverpool Street London, and updated the date to be 2022

        "What will the delay be at Southampton if the train was delayed 5 minutes from Weymouth?",

        "What will the delay be at Southampton if the train was delayed by 4 hours from Weymouth?",

        "What is the predicted delay at Southampton if my train was 3 minutes late from Weymouth?",

        "What is the cheapest single ticket for six adults and one child from Milton Keynes Central to Norwich, arriving for 11:00 on 30/2/2022"  # TODO Updated to be in the future, it can't read the time for some reason
    ]
    #displacy.serve(nlp(queries[2]), style="dep", port=16000)


    for query in queries:
        response = parse_query(query)
        print(response)
