from fuzzywuzzy import process
from datetime import datetime
import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_sm')


def load_stations():
    data = {}
    with open('../../resources/stations.csv') as fp:
        fp.readline()  # throw away first line
        for line in fp:
            fields = line.split(',')
            data[fields[0].lower()] = fields[3].lower()
    return data


station_map = load_stations()


def get_matching_stations(station_text):
    return process.extract(station_text, station_map.keys())


def extract_station_name(token):
    ntoken = token.doc[token.i + 1]
    name = ntoken.text

    while ntoken.dep_ == 'compound':
        ntoken = ntoken.doc[ntoken.i + 1]
        name += ' ' + ntoken.text
    return name


def extract_journey_time(token):
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


units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
        ]

def extract_persons(token):
    ntoken = token.doc[token.i - 1]
    if ntoken.dep_ == 'nummod':
        try:
            return units.index(ntoken.text)
        except ValueError:
            return int(ntoken.text)
    return 1


nlp = spacy.load('en_core_web_sm')

# query = "What is the cheapest ticket for a return from Milton Keynes Central to Norwich, arriving by 13:00 on 15/1/2021"
query = "What is the cheapest ticket for four adults and 2 children from Milton Keynes Central to Norwich, " \
        "arriving by 13:00 on 15/1/2021 "

doc = nlp(query)
response = {'from': None, 'to': None, 'arrive': True, 'time': datetime.now(), 'type': 'single', 'adult': 1, 'child': 0}

for token in doc:
    if token.pos_ == 'VERB':
        if token.lemma_ == 'depart':
            response['arrive'] = False
        response['time'] = extract_journey_time(token)
    elif token.pos_ == 'NOUN':
        if token.text.lower() == 'return':
            response['type'] = 'return'
        elif token.lemma_ == 'adult':
            response['adult'] = extract_persons(token)
        elif token.lemma_ == 'child':
            response['child'] = extract_persons(token)
    elif token.pos_ == 'ADP':
        if token.lemma_ == 'from':
            response['from'] = extract_station_name(token)
        elif token.lemma_ == 'to':
            response['to'] = extract_station_name(token)

print(response)
displacy.serve(doc, style="dep", port=20000)
