
#
# NLTK based functions
#
#

import nltk
import string
import re

from collections import defaultdict
from nltk.util import ngrams


# tokenize, remove stop words and do stemming for a string
# returns a list object
def tokenize0(text):
    textLower = text.lower()
    # get a list of tokens from a string with a simple tokenizer (spaces)
    tokens = nltk.wordpunct_tokenize(textLower)
    # setup stem
    stem = nltk.stem.SnowballStemmer('english')
    # setup stopwords
    stopWords = set(nltk.corpus.stopwords.words('english'))
    stems = []
    for token in tokens:
        # skip punctuation
        if token in string.punctuation: continue
        # skip stop words
        if token in stopWords: continue
        # stemming each token
        stems.append(stem.stem(token))
    return stems

# an extra function for the next one
# https://www.geeksforgeeks.org/python-lemmatization-approaches-with-examples/
def pos_tagger1(nltk_tag):
    if nltk_tag.startswith('J'):
        return nltk.corpus.wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return nltk.corpus.wordnet.VERB
    elif nltk_tag.startswith('N'):
        return nltk.corpus.wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return nltk.corpus.wordnet.ADV
    else:
        return None
# tokenize, remove stop words and do lemming for a string 
#   (it seems lemming is not fully correct)
# returns a list object
def tokenize1(text):
    textLower = text.lower()
    # remove urls & some special symbols
    textLower = re.sub('http[s]?://\S+', '', textLower)
    textLower = re.sub(r'[()]', '', textLower)
    textLower = re.sub('[<!@#$/>]', '', textLower)
    # get a list of tokens from a string with a simple tokenizer (spaces)
    tokens = nltk.wordpunct_tokenize(textLower)
    # get a list of tags (parts of speech) for the tokens
    tags = nltk.pos_tag(tokens, lang='eng')
    # create lemmatizer
    lemmatizer = nltk.stem.WordNetLemmatizer()
    # setup stopwords
    stopWords = set(nltk.corpus.stopwords.words('english'))
    lems = []
    for (token,tag) in tags:
        # skip punctuation
        if token in string.punctuation: continue
        # skip stop words
        if token in stopWords: continue
        # convert tag with a different function - lemmantizer understands that format 
        # (see https://www.geeksforgeeks.org/python-lemmatization-approaches-with-examples/)
        mytag = pos_tagger1(tag)
        if mytag is None: 
            # lemmantize the token without tag
            lems.append(lemmatizer.lemmatize(token))
        else:
            # lemmantize the token using tag
            lems.append(lemmatizer.lemmatize(token,mytag)) 
    return lems


# a dictionary of word counts in a tokens list
# features[token] = number
def vectorize(tokens):
    features = defaultdict(int)
    for token in tokens:
        features[token]+=1
    return features


# get ngrams from text
def ngrams2(text,n):
    sents = nltk.sent_tokenize(text)
    arr = []
    for sent in sents:
        tokens = tokenize1(sent)
        arr.extend(list(ngrams(tokens,n)))
    return arr

# remove urls and extra symbols from string
def removeURLs(text):
    text = re.sub('http[s]?://\S+', '', text)
    text = re.sub(r'[()]', '', text)
    text = re.sub(r'[\[\]]', '', text)
    text = re.sub('[<!@#$/>]', '', text)
    text = re.sub(r'[-]','',text)
    return text