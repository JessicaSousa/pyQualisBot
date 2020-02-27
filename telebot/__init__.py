
from .bot import init
import pickle


def run_bot():
    init()
    
    #from .qualis_chat.rasa.inv_index import save_inverted_indexes, load_inverted_indexes
    #data = load_inverted_indexes()
    #save_inverted_indexes(data)




if __name__ == '__main__':
    run_bot()