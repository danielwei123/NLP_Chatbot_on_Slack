# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from nltk import tokenize 
import nltk.data
from autocorrect import spell
import string
import re
import db
import pymysql

bot_words= ["bot1", "bot2", "bot3", "bot4", "robot1", "robot2", "robot3", "robot4", "Bot1", "Bot2", "Bot3", "Bot4", "Robot1", "Robot2", "Robot3", "Robot4"]
stopwords = ["robot", "turtlebot", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "further", "then", "once", "here", "there", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should"]
caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


# extract bot number info, return type is a list of string
def get_bot_num(strs):

    findbots=re.findall(r'(bot1|bot2|bot3|bot4)',strs )

    return ([s.replace('bot', '') for s in findbots])

# cleaning data
def clean_word(sentence):

    ps = PorterStemmer()
    wordnet = WordNetLemmatizer()

    # remove punctuation
    sentence = re.sub(r'[^\w\s]','',sentence)

    # tokenization and make sure all the words are lower case
    words = word_tokenize(sentence.lower())

    # correct misspelling words
    words = [spell(x) for x in words]

    # filter stopwords
    words = [word for word in words if word not in stopwords]
    # print('words: ', words)

    # lemmatizing
    lemmatized_words = [wordnet.lemmatize(word) for word in words]
    # print('lemmatized_words: ', lemmatized_words)

    # stemming
    stemmed_words = [ps.stem(word) for word in lemmatized_words]
    # print('stemmed_words: ', stemmed_words)

    # delete repetitive words
    return set(stemmed_words)


# choose nouns from user's input sentence
def search_location(sentence):
    
    sentence = re.sub(r'[^\w\s]','',sentence)
    words = word_tokenize(sentence)
    words = [word for word in words if word not in stopwords]
    results = [wordset[0] for wordset in nltk.pos_tag(words) if wordset[1] in ['NN', 'NNP', 'NNS']]

    name = db.search_by_name(results)
    
    if name != False:
        return db.center_coord(name)

    return

#split a paragraph into a list of sentences
def splitSentence(paragraph):

    return tokenize.sent_tokenize(paragraph)

def remove_bot_num(string):
    str_temp = string
    for i in bot_words:
        str_temp = str_temp.replace(i,'')
    return str_temp

# split a paragraph into a list of sentences
def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


# testing sentences

# print(split_into_sentences('Move to Kiva, take a picture. Turn 360.'))
# print(remove_bot_num('bot1 and bot2, move 3 m. Rotate 304. Move 2 m.'))
# string = 'bot1 and bot2, move 3 meter. Rotate 304 degree. Move 2 m.'
# print(remove_bot_num(string))
# string = remove_bot_num(string)
# print(splitSentence(string))