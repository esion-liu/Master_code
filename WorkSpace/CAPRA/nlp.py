# this file uses stanford natural language toolkit for sentiment analysis
import stanza
import numpy as np

nlp = stanza.Pipeline('en', processors='tokenize,sentiment')

def sentiment_extractor(text):
    """
    Folling the method mentioned in the CAPRA paper, which is the average sentiment in each sentences
    """
    doc = nlp(text)
    
    num_pos = 0
    num_neg = 0
    num_neu = 0
    for s in doc.sentences:
        if s.sentiment == 0:
            num_neg += 1
        elif s.sentiment == 1:
            num_neu += 1
        else:
            num_pos += 1
    return (num_neg * (-1.0) + num_pos * 1.0) / (num_pos + num_neu + num_neg)

def feature_extractor(text):
    """
    This function is used for review usefulness measurement
    Extraction feature includes:
    1. number of words
    2. average review sentiment of other reivews by the same user
    3. Sum of sentiments the total number of sentiments that has been discussed in the review
    """
    
    doc = nlp(text)
    num_word = doc.num_tokens
    
    num_pos_sen = 0
    num_neg_sen = 0
    num_neu_sen = 0
    # tags in toolkit: 0 negative; 1 neutural; 2 positive
    for s in doc.sentences:
        if s.sentiment == 0:
            num_neg_sen += 1
        elif s.sentiment == 1:
            num_neu_sen += 1
        else:
            num_pos_sen += 1
    SoS = (num_pos_sen + num_neg_sen) / (num_neg_sen + num_neu_sen + num_pos_sen)

    feature_vec = [num_word, num_pos_sen, num_neu_sen, num_neg_sen, SoS]
    return feature_vec