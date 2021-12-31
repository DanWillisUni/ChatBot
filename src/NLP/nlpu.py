import spacy
from spacy import *
import re
import json


class NLPU:
    def __init__(self, stems_path):
        self.nlp = spacy.load("en_core_web_md")



