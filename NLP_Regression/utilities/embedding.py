from gensim.models import Word2Vec
import os.path as path

MODELS_DIR = "word2vecmodels/"


def load_model(name) -> Word2Vec:
    model_dir = MODELS_DIR + name + '.model'
    if path.isfile(model_dir):
        return Word2Vec.load(model_dir)
    else:
        raise Exception('No such Word2Vector model exist')
    
def train_model(name, ) -> None:
    pass

