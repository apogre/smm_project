# -*- coding: utf-8 -*- 

import nltk
from nltk.tree import *
import cPickle as pickle
import csv
import sys
import dateutil.parser as dp
import sparql

objects = []
relation=[]
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


entities = {} 
resources = {}
def resource_extractor(labels):
    for i,label in enumerate(labels):
        resource_list = []
        if label[1] != 'DATE':
            label = label[0]
            q = ('select distinct ?x where{?x rdfs:label "'+ label +'"@en }')
            # print q
            result = sparql.query('http://dbpedia.org/sparql', q)
            # print result
            types = {}
            for row in result:
                values = sparql.unpack_row(row)
                if not 'Category:' in values[0]:
                    # print values[0]
                    resource_list.append(values[0])
                    my_list = []
                    q1=('SELECT distinct ?type ?superType WHERE  { <'+str(values[0]) + '> rdf:type ?type . optional { ?type rdfs:subClassOf ?superType } }')
                    result1 = sparql.query('http://dbpedia.org/sparql', q1)
                    for row1 in result1:
                        values1 = sparql.unpack_row(row1)
                        my_list.append(values1)
                    types[values[0]]= my_list
            entities[i] = types
            resources[label] = resource_list
    return resources
            # print resources

def relation_extractor(resources):
    for i in range(len(resources)):
        # print ent
        print resources
        if str(ent[i][0]) in resources:
            for item1 in resources[ent[i][0]]:
                # print item1
                if str(ent[i+1][0]) in resources:
                    for item2 in resources[ent[i+1][0]]:
                        print item2
                        q1=('SELECT ?r WHERE  { <'+str(item1) + '> ?r <' +str(item2)+'>}')
                        print q1
                        try:
                            if 'wikidata' in item1 and 'wikidata' in item2:
                                result1 = doSparqlQuery(q1)
                                data = result1['results']['bindings'][0]
                                print([str(item1),str(data['r']['value']),str(item2)])
                                print '\n'
                                rel =  data['r']['value'].split('/')
                                relation.append(rel[-1])
                            elif 'dbpedia' in item1 and 'dbpedia' in item2:
                                result1 = sparql.query('http://dbpedia.org/sparql', q1)
                                for row1 in result1:
                                    values1 = sparql.unpack_row(row1)
                                    if values1:
                                        print([str(item1),str(values1[0]),str(item2)])
                                        print '\n'
                                        rel =  values1[0].split('/')
                                        relation.append(rel[-1])
                            print relation
                                        # writer.writerow([str(item1),str(values1[0]),str(item2)])  
                                    # relation.append(values1[0])
                        except:
                            pass    


with open('obama_sample.txt','r') as f:
    para = f.readline()
    for i,row in enumerate(para.split('.')):
        print i
        print row
        if row:
            doc = row
            # doc = doc.replace('RT','')
            # try:
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
            # print ent
            resources = resource_extractor(ent)
            relation_extractor(resources)
            objects.extend(ent)
        # except:
            #     pass
                # with open('logs.csv','ab') as csvf:
                #     swriter = csv.writer(csvf)
                #     swriter.writerow(row)
# print resources

# print entities
# with open('entity.txt','wb') as fp:
#     pickle.dump(objects,fp)