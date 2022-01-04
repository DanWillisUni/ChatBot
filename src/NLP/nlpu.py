import spacy
import json


class NLPU:
    def __init__(self, stems_path):
        self.nlp = spacy.load("en_core_web_md")
        # open and load stems.json
        with open('stemming/stems.json') as fp:
            stems_path = json.load(fp)

