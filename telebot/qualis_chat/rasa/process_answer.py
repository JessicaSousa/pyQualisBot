from rasa.cli.utils import get_validated_path
from rasa.constants import DEFAULT_MODELS_PATH
from rasa.model import get_model, get_model_subdirectories
import rasa.nlu.run
import asyncio
import logging
import typing
from typing import Optional, Text
from rasa.cli.utils import print_success
from rasa.core.interpreter import INTENT_MESSAGE_PREFIX, RegexInterpreter
from rasa.nlu.model import Interpreter
from rasa.nlu.utils import json_to_string
if typing.TYPE_CHECKING:
    from rasa.nlu.components import ComponentBuilder
from rasa.cli.utils import get_validated_path
from rasa.constants import DEFAULT_MODELS_PATH
from rasa.model import get_model, get_model_subdirectories
import rasa.nlu.run
import pickle
import numpy as np
import pandas as pd


from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


############################################  INVERTED INDEXES  ############################################
import nltk
from collections import defaultdict
from nltk.stem.snowball import EnglishStemmer  # Assuming we're working with English
import pickle 
import os


_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_area_name_correct(area_name,area_model,codes2Name,count_vect,tf_transformer):
    x = count_vect.transform(np.array([area_name]))
    #x = tf_transformer.transform(x)
    #print('x:',x)
    code = area_model.predict(x)
    correct_name = codes2Name[code[0]]
    return correct_name

class ChatQualisBot:
    def __init__(self):
        filename = "inverted_indexes.b"
        self.inverted_indexes = pickle.load(open(os.path.join(_ROOT, filename),'rb'))

############################################  NLU MODEL  ############################################

        self.areas = {'administração':0,'administração pública':0,'administração de empresas':0,'contábeis':0,'ciências contábeis':0,'turismo':0,'antropologia':1,'arqueologia':1,'arquitetura':2,'urbanismo':2,'design':3,'artes':3,'astronomia':4,'física':4,'biodiversidade':5,'biotecnologia':6,'ciência da computação':7,'computação':7,'ciência de alimentos':8,'alimentos':8,'ciência política':9,'política':9,'relações internacionais':9,'relações':9,'ciências agrárias i':10,'ciências ambientais':11,'ambientais':11,'biológicas i':12,'biológicas ii':13,'biológicas iii':14,'ciências biológicas i':12,'ciências biológicas ii':13,'ciências biológicas iii':14,'ciências da religião e teologia':15,'religião':15,'teologia':15,'comunicação e informação':16,'comunicação':16,'informação':16,'direito':17,'economia':18,'educação':19,'educação física':20,'enfermagem':21,'engenharias i':22,'engenharias ii':23,'engenharias iii':24,'engenharias iv':25,'ensino':26,'farmácia':27,'filosofia':28,'geociências':29,'geografia':30,'história':31,'interdisciplinar':32,'linguística':33,'literatura':33,'linguística e literatura':33,'matemática':34,'probabilidade':34,'estatística':34,'materiais':35,'medicina i':36,'medicina ii':37,'medicina iii':38,'medicina veterinária':39,'nutrição':40,'odontologia':41,'odonto':41,'dentistaria':41,'planejamento':42,'planejamento urbano':42,'planejamento regional':42,'demografia':42,'psicologia':43,'química':44,'saúde coletiva':45,'serviço social':46,'sociologia':47,'zootecnia':48,'recursos pesqueiros':48}
        self.areas_codes= dict()
        for key, value in self.areas.items():
            self.areas_codes.setdefault(value, list()).append(key)
            
        print(DEFAULT_MODELS_PATH)
        
        model = get_validated_path('', "model", DEFAULT_MODELS_PATH)

        try:
            model_path = get_model(model)
        except ModelNotFound:
            print_error(
                "No model found. Train a model before running the "
                "server using `rasa train nlu`."
            )
        
        _, nlu_model = get_model_subdirectories(model_path)
        
        if not nlu_model:
            print_error(
                "No NLU model found. Train a model before running the "
                "server using `rasa train nlu`."
            )

        #rasa.nlu.run.run_cmdline(nlu_model)
        print(nlu_model)
        self.model_path = nlu_model
        self.interpreter = Interpreter.load(self.model_path, None)
        self.regex_interpreter = RegexInterpreter()

        print_success("NLU model loaded. Type a message and press enter to parse it.")

        ############################################  CORRECT AREA CLASSIFIER  ############################################

        
        self.area_model = pickle.load(open(os.path.join(_ROOT,"..", "area_model.b"), 'rb'))
        self.count_vect = pickle.load(open(os.path.join(_ROOT,"..", "count_vect.b"), 'rb'))
        self.tf_transformer = pickle.load(open(os.path.join(_ROOT,"..", "tf_transformer.b"), 'rb'))

        self.codes2Name = pickle.load(open(os.path.join(_ROOT, "codes2Name.b"), 'rb'))
        self.quadrien = pd.read_csv(os.path.join(_ROOT, "quadrien.csv"))

    
    def get_answer(self,message):
        if message.startswith(INTENT_MESSAGE_PREFIX):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(self.regex_interpreter.parse(message))
        else:
            result = self.interpreter.parse(message)
        #print(result)
        entities = result['entities']
        print(entities)
        state=0
        area_names=[]
        search_terms=[]

        area_count=0
        termo_count=0
        if(len(entities)>0):
            for ent in entities:
                if(ent['entity']=='area'):
                    area_names.append((ent['value'],ent['confidence']))
                    area_count+=1
                if(ent['entity']=='termo'):
                    search_terms.append((ent['value'],ent['confidence']))
                    termo_count+=1
            if(area_count>0 and termo_count==0):
                best_area_name =''
                best_area_conf = -9990
                for name in area_names:
                    if name[1]>best_area_conf:
                        best_area_conf = name[1]
                        best_area_name = name[0]
                area_name = get_area_name_correct(best_area_name,self.area_model,self.codes2Name,self.count_vect,self.tf_transformer)
                #So tem area, n tem termos. Retorna a tabela da area de avaliacao
                return 1,self.quadrien[self.quadrien["Área de Avaliação"]==area_name[0]]
            area_name = area_names[0][0]
            area_name = get_area_name_correct(area_name,self.area_model,self.codes2Name,self.count_vect,self.tf_transformer)
            try:
                #tem area e termo
                search_term = search_terms[0][0]
                return 0,self.inverted_indexes[area_name[0]].lookup(search_term)
            except TypeError:
                print("term not found in search!")
            return  2,None
            
