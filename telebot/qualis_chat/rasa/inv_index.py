import nltk
from collections import defaultdict
from nltk.stem.snowball import EnglishStemmer  # Assuming we're working with English
import pickle
import os

nltk.download('stopwords')
nltk.download('punkt')

_ROOT = os.path.abspath(os.path.dirname(__file__))

class Index:
    """ Inverted index datastructure """
 
    def __init__(self, tokenizer=None, stemmer=None, stopwords=None):
        """
        tokenizer   -- NLTK compatible tokenizer function
        stemmer     -- NLTK compatible stemmer 
        stopwords   -- list of ignored words
        """
        self.tokenizer = nltk.word_tokenize
        self.stemmer = EnglishStemmer()
        self.index = defaultdict(list)
        self.documents = {}
        self.__unique_id = 0
        if not stopwords:
            self.stopwords = set()
        else:
            self.stopwords = set(nltk.corpus.stopwords.words('english'))
 
    def lookup(self, word):
        """
        Lookup a word in the index
        """
        word = word.lower()
        if self.stemmer:
            word = self.stemmer.stem(word)
 
        return [self.documents.get(id, None) for id in self.index.get(word)]
 
    def add(self, document):
        """
        Add a document string to the index
        """
        for token in [t.lower() for t in nltk.word_tokenize(document)]:
            if token in self.stopwords:
                continue
 
            if self.stemmer:
                token = self.stemmer.stem(token)
 
            if self.__unique_id not in self.index[token]:
                self.index[token].append(self.__unique_id)
 
        self.documents[self.__unique_id] = document
        self.__unique_id += 1 
           


def save_inverted_indexes(data):
    write_file = open(os.path.join(_ROOT, "inverted_indexes.b"), 'wb')
    pickle.dump(data, write_file)


def load_inverted_indexes():
    read_file = open(os.path.join(_ROOT, "inverted_indexes.b"), 'rb')
    return pickle.load(read_file)
