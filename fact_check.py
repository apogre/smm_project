# -*- coding: utf-8 -*- 

import nltk
from nltk.tree import *
import cPickle as pickle
import csv
import sys
import dateutil.parser as dp

objects = []
ROOT = 'ROOT'
SPARQL_SERVICE_URL = 'https://query.wikidata.org/sparql'

# grammar = r"""
#         NP: {<DT>?<JJ.*>*<NN.*>+}
#             {}
#     """
# cp = nltk.RegexpParser(grammar)



def ie_preprocess(doc):
    sentences = nltk.sent_tokenize(doc)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences] 
    return sentences

def getNodes(parent):
    entities = []
    for node in parent:
        if type(node) is Tree:
            if node.label() == ROOT:
                pass
            elif node.label() == 'DATE' or node.label() == 'ORGANIZATION' or node.label() =='PERSON' or node.label() =='LOCATION' or node.label() =='FACILITY' or node.label() =='GPE':
                entity = node.leaves()
                entity = ' '.join(e[0] for e in entity)
                # print node.label(), node
                # print index_list.index(entity)
                tup = (entity, node.label())
                entities.append(tup)
            else:
                pass
            getNodes(node)
        else:
            pass
    return entities

def date_parser(doc):
    return dp.parse(doc,fuzzy=True)

def resource_extractor(lables):
    for i,label in enumerate(labels):
    resource_list = []
    print label
    print "==========="
    q = ('select distinct ?x where{?x rdfs:label'+ label +' }')
    result = sparql.query('http://dbpedia.org/sparql', q)
    types = {}
    for row in result:
        values = sparql.unpack_row(row)
        if not 'Category:' in values[0]:
            print values[0]
            resource_list.append(values[0])
            my_list = []
            q1=('SELECT distinct ?type ?superType WHERE  { <'+str(values[0]) + '> rdf:type ?type . optional { ?type rdfs:subClassOf ?superType}}')
            result1 = sparql.query('http://dbpedia.org/sparql', q1)
            for row1 in result1:
                values1 = sparql.unpack_row(row1)
                my_list.append(values1)
            types[values[0]]= my_list
    entities[i] = types
    resources[label] = resource_list    
print "==========="


with open('obama_sample.txt','r') as f:
    para = f.readline()
    for i,row in enumerate(para.split('.')):
        print i
        print row
        doc = row
        # doc = doc.replace('RT','')
        try:
            tagged = ie_preprocess(doc)
            # word_list = doc.split()
            # print word_list
            # print tagged
            # sys.exit()
            tree = nltk.ne_chunk(tagged[0])
            print tree
            # tree = Tree.fromstring(str(tree)
            ent =  getNodes(tree)
            try:
                date = date_parser(doc)
                tup1 = (date,'DATE')
                ent.append(tup1)
            except:
                pass
            print ent
            objects.extend(ent)
        except:
            pass
            # with open('logs.csv','ab') as csvf:
            #     swriter = csv.writer(csvf)
            #     swriter.writerow(row)


# print entities
# with open('entity.txt','wb') as fp:
#     pickle.dump(objects,fp)