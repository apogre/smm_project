# -*- coding: utf-8 -*- 

import nltk
from nltk.tree import *
import cPickle as pickle
import csv
import sys
import dateutil.parser as dp
import sparql
import urllib2
import json
from difflib import SequenceMatcher

objects = []
relation=[]
ROOT = 'ROOT'
SPARQL_SERVICE_URL = 'https://query.wikidata.org/sparql'
global date_flag
date_flag = 0

# grammar = r"""
#         NP: {<DT>?<JJ.*>*<NN.*>+}
#             {}
#     """
# cp = nltk.RegexpParser(grammar)
# select ?p ?o where {
#   ?p a owl:DatatypeProperty ;
#      rdfs:range xsd:date .
#  <http://dbpedia.org/resource/Barack_Obama> ?p ?o .
# }
# SELECT distinct ?uri ?label
# WHERE {
#    ?uri rdfs:label ?label .
#    FILTER regex(str(?label), "Barack Hussein Obama", "i")
# }
# q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . ?uri rdf:type foaf:'+ str(label[1].title()) + ' . FILTER (regex(str(?label),"'+ str(label[0]) +'", "i") && langMatches(lang(?label),"EN") )} limit 100')


def similar(a,b):
    return SequenceMatcher(None,a,b).ratio()

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
new_labels = []
def resource_extractor(labels):
    for i,label in enumerate(labels):
        resource_list = []
        if label[1] != 'DATE':
            label = label[0]
            new_labels.append(label)
            q = ('select distinct ?x where{?x rdfs:label "'+ label +'"@en }')
            # print q
            result = sparql.query('http://dbpedia.org/sparql', q)
            # print result
            types = {}
            for row in result:
                values = sparql.unpack_row(row)
                if not 'Category:' in values[0] or 'alumni' in values[0]:
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
    print types        
    return resources
            # print resources

def resource_extractor_updated(labels):
    print labels
    for i,label in enumerate(labels):
        resource_list = []
        score_list = {}
        if label[1] != 'DATE':
            print label
            # if label[1] == 'GPE':
            # label = label[0]
            new_labels.append(label)
            q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . FILTER(regex(str(?label),"'+ str(label[0]) +'", "i") && langMatches(lang(?label),"EN") )} limit 100')
            result = sparql.query('http://dbpedia.org/sparql', q_u)
            # print result
            # types = {}
            for row in result:
                values = sparql.unpack_row(row)
                print values
                if not 'Category:' in values[0] or 'alumni' in values[0]:
                    print values[0]
                    score = similar(values[1],label[0])
                    score_list[score] = values
                    # resource_list.append(values[0])
                    # my_list = []
                    # q1=('SELECT distinct ?type ?superType WHERE  { <'+str(values[0]) + '> rdf:type ?type . optional { ?type rdfs:subClassOf ?superType } }')
                    # result1 = sparql.query('http://dbpedia.org/sparql', q1)
                    # for row1 in result1:
                    #     values1 = sparql.unpack_row(row1)
                    #     my_list.append(values1)
                    # types[values[0]]= my_list
            # entities[i] = types
            resources[label[0]] = score_list
            # print resources
    # print types        
    return resources


def relation_extractor(resources):
    print new_labels
    # sys.exit()
    # print resources
    print "====Relations===="
    my_item1 = []
    my_item2 = []
    for i in range(0,len(resources)):
        print new_labels[i][0]
        if str(new_labels[i][0]) in resources:
            for item1_k,item1_v in resources[new_labels[i][0]].iteritems():
                if 'dbpedia' in item1_v[0]:
                    link = urllib2.urlopen(item1_v[0])
                    url1 = link.geturl()
                    url1 = url1.replace('page','resource')
                # print item1
                for j in range(i+1,len(resources)):
                    if str(new_labels[j][0]) in resources:
                        for item2_k,item2_v in resources[new_labels[j][0]].iteritems():
                            if 'dbpedia' in item2_v[0]:
                                link = urllib2.urlopen(item2_v[0])
                                url2 = link.geturl()
                                url2 = url2.replace('page','resource')
                            # print item2
                            q1=('SELECT ?r WHERE  { <'+str(url1) + '> ?r <' +str(url2)+'>}')
                            # print q1
                            try:
                                # if 'wikidata' in item1 and 'wikidata' in item2:
                                #     print q1
                                #     result1 = doSparqlQuery(q1)
                                #     data = result1['results']['bindings'][0]
                                #     print([str(item1),str(data['r']['value']),str(item2)])
                                #     print '\n'
                                #     rel =  data['r']['value'].split('/')
                                #     relation.append(rel[-1])
                                if url1 not in my_item1 and url2 not in my_item2:
                                    if 'dbpedia' in url1 and 'dbpedia' in url2:
                                        result1 = sparql.query('http://dbpedia.org/sparql', q1)
                                        print q1
                                        my_item1.append(url1)
                                        my_item2.append(url2)
                                        for row1 in result1:
                                            values1 = sparql.unpack_row(row1)
                                            if values1:
                                                print([str(url1),str(values1[0]),str(url2)])
                                                print '\n'
                                                rel =  values1[0].split('/')
                                                relation.append(rel[-1])
                                    # print relation
                                                # writer.writerow([str(item1),str(values1[0]),str(item2)])  
                                            # relation.append(values1[0])
                            except:
                                pass 

def date_extractor(date,resources):
    # print resources
    for key,val in resources.iteritems():
        for v in val:
            # print v
            if 'dbpedia' in v:
                link = urllib2.urlopen(v)
                v = link.geturl()
                v = v.replace('page','resource')
                dq=('SELECT distinct ?r ?o WHERE  {  ?r a owl:DatatypeProperty ; rdfs:range xsd:date . <'+str(v) + '> ?r ?o .}')
                resultd = sparql.query('http://dbpedia.org/sparql', dq)
                # print resultd
                for i,row1 in enumerate(resultd):
                    # print i
                    values1 = sparql.unpack_row(row1)
                    
                    if values1[1] == date.date():
                        print v,values1
                    # resources[key].extend(values1)


with open('obama_sample.txt','r') as f:
    para = f.readline()
    for i,row in enumerate(para.split('.')):
        print i
        print row
        # try:
        if row:
            doc = row
            
            tagged = ie_preprocess(doc)
            # print tagged
            tree = nltk.ne_chunk(tagged[0])
            print "====Tree===="
            print tree
            # tree = Tree.fromstring(str(tree)
            ent =  getNodes(tree)
            # print ent
            updated_labels = []
            for en in ent:
                if 'University' in en[0] or 'College' in en[0] or 'School' in en[0]:
                    label1 = str(en[0])+' alumni'
                    tup2 = (label1,en[1])
                    # print tup2
                    updated_labels.append(tup2)
            ent.extend(updated_labels)

            try:
                date = date_parser(doc)
                tup1 = (date,'DATE')
                ent.append(tup1)
                date_flag = 1
            except:
                pass
            print "====Entities===="
            # print ent
            # sys.exit()
            # resources = resource_extractor(ent)
            resources = resource_extractor_updated(ent)
            print resources
            # print date_flag
            relation_extractor(resources)
            # if date_flag == 1:
            #     date_extractor(date,resources)
            #     date_flag = 0
            # objects.extend(ent)
        # except:
        #         pass
                # with open('logs.csv','ab') as csvf:
                #     swriter = csv.writer(csvf)
                #     swriter.writerow(row)
# print resources

# print entities
# with open('entity.txt','wb') as fp:
#     pickle.dump(objects,fp)