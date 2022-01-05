import spacy



class NLPU:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        # open and load stems.json
        '''with open('stemming/stems.json') as fp:
            stems_path = json.load(fp)'''



