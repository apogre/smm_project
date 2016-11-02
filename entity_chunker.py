# -*- coding: utf-8 -*- 

import nltk
from nltk.tree import *
import cPickle as pickle
import csv
import sys

objects = []
ROOT = 'ROOT'
grammar = r"""
        NP: {<DT>?<JJ.*>*<NN.*>+}
            {}
    """
cp = nltk.RegexpParser(grammar)

def ie_preprocess(doc):
    sentences = nltk.sent_tokenize(doc)
    print sentences
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    print sentences
    sentences = [nltk.pos_tag(sent) for sent in sentences] 
    print sentences
    return sentences

def getNodes(parent):
    entities = []
    for node in parent:
        if type(node) is Tree:
            if node.label() == ROOT:
                pass
            elif node.label() == 'ORGANIZATION' or node.label() =='PERSON' or node.label() =='LOCATION' or node.label() =='FACILITY' or node.label() =='GPE':
                entity = node.leaves()
                # print entity
                entity = ' '.join(e[0] for e in entity)
                if '@' in entity:
                    entity = ''.join(entity.split(' '))
                entities.append(entity)
            else:
                pass
            getNodes(node)
        else:
            pass
    return entities


with open('tweet.csv','rb') as csvfile:
    reader = csv.reader(csvfile)
    for i,row in enumerate(reader):
        print i
        doc = row[0]
        doc = doc.replace('RT','')
        try:
            tagged = ie_preprocess(doc)
            # print tagged
            # sys.exit()
            tree = nltk.ne_chunk(tagged[0])
            print tree
            # print tree
            # tree = Tree.fromstring(str(tree)
            ent =  getNodes(tree)
            # print ent
            objects.extend(ent)
        except:
            with open('logs.csv','ab') as csvf:
                swriter = csv.writer(csvf)
                swriter.writerow(row)


# print entities
# with open('entity.txt','wb') as fp:
#     pickle.dump(objects,fp)