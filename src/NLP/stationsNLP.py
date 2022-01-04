from fuzzywuzzy import process
from nlpu import NLPU
from spacy import *


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


def parse_stations(sentence):

    # document to parse
    doc = NLPU(sentence)

    '''
    Create a dictionary of station information given by user
    Starting station, destination station, or a station that couldn't be matched
    '''
    stations = {"from_station": None,
                "to_station": None,
                "no_match": None}






if __name__ == '__main__':
    print(get_matching_stations('miltan keynes'))
