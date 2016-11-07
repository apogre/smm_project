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
import datetime
from string import digits
from nltk.tag import StanfordNERTagger
from itertools import groupby
from pprint import pprint

st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')


objects = []
relation=[]
ROOT = 'ROOT'
SPARQL_SERVICE_URL = 'https://query.wikidata.org/sparql'
global date_flag
date_flag = 0

# export CLASSPATH=/home/wolfgang/Downloads/stanford-ner-2015-04-20/stanford-ner-3.5.2.jar
# export STANFORD_MODELS=/home/wolfgang/Downloads/stanford-ner-2015-04-20/classifiers

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

def get_nodes_updated(netagged_words):
    ent = []
    for tag, chunk in groupby(netagged_words, lambda x:x[1]):
        if tag != "O":
            tuple1 =(" ".join(w for w, t in chunk),tag)
            ent.append(tuple1)
    return ent

def similar(a,b):
    return SequenceMatcher(None,a,b).ratio()

def date_parser(doc):
    return dp.parse(doc,fuzzy=True)


entities = {} 
resources = {}
new_labels = []

def resource_extractor_updated(labels):
    # print labels
    for i,label in enumerate(labels):
        resource_list = []
        score_list = {}
        if label[1] != 'DATE':
            # print label
            # if label[1] == 'GPE':
            # label = label[0]
            new_labels.append(label)
            q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . FILTER(regex(str(?label),"' +str(label[0]) +'", "i") && langMatches(lang(?label),"EN") )} limit 15')
            # print q_u
            result = sparql.query('http://localhost:8890/sparql', q_u)
            # print result
            # types = {}
            for row in result:
                values = sparql.unpack_row(row)
                # print values[0]
                if not 'Category:' in values[0] and not 'wikidata' in values[0]:
                    try:
                        q_type=('SELECT distinct ?type WHERE  { <'+str(values[0].encode('utf-8')) + '> rdf:type ?type }')
                        result_type = sparql.query('http://localhost:8890/sparql', q_type)
                        type_list = []
                        # print q_type
                        for row_type in result_type:
                            types1 = sparql.unpack_row(row_type)
                            # print types1
                            mytype =  types1[0].split('/')[-1]
                            types = str(mytype).translate(None,digits)
                            # print types
                            if '#' in types:
                                types = types.split('#')[-1]
                            type_list.append(types)
                        type_list = list(set(type_list))
                        if 'Q' in type_list:
                            type_list.remove('Q')
                        # print type_list
                        score = similar(values[1],label[0])
                        # print score
                        values.append(type_list)
                        if score in score_list:
                            score_list[score].append(values)
                        else:
                            score_list[score] = [values]
                    except:
                        pass
            # q = ('select distinct ?x where{?x rdfs:label "'+ label[0] +'"@en }')
            # result = sparql.query('http://localhost:8890/sparql', q)
            # for row in result:
            #     values = sparql.unpack_row(row)
            #     if not 'Category:' in values[0] or 'alumni' in values[0]:
            #         # print values[0]
            #         # resource_list.append(values[0])
            #         q1=('SELECT distinct ?type WHERE  { <'+str(values[0].encode()) + '> rdf:type ?type }')
            #         print q1
            #         result1 = sparql.query('http://localhost:8890/sparql', q1)
            #         type_list = []
            #         for row1 in result1:
            #             values1 = sparql.unpack_row(row1)
            #             mytype =  values1[0].split('/')[-1]
            #             types = str(mytype).translate(None,digits)
            #             if '#' in types:
            #                 types = types.split('#')[-1]
            #             type_list.append(types)
            #         main_value = [values[0],label[0],type_list]
            #         if 1.0 in score_list:
            #             score_list[1.0].append(main_value)
            #         else:
            #             score_list[1.0] = [main_value]
            resources[label[0]] = score_list
    return resources


def relation_extractor(resources):
    print new_labels
    # sys.exit()
    # print resources
    print "====Relations===="
    my_item1 = []
    my_item2 = []
    for i in range(0,len(resources)-1):
        # print new_labels[i][0]
        if str(new_labels[i][0]) in resources:
            keylist_1 = resources[new_labels[i][0]].keys()
            keylist_1.sort(reverse=True)
            # print keylist_1
            for key1 in keylist_1:
                # print key1
                item1_v = resources[new_labels[i][0]][key1]
                # print item1_v
                for i1 in item1_v:
                    # print i1
                    if 'dbpedia' in i1[0]:
                        try:
                            link = urllib2.urlopen(i1[0])
                            url1 = link.geturl()
                            url1 = url1.replace('page','resource')
                        except:
                            url1 = i1[0]
                        print "====================="
                        print url1
                    for j in range(i+1,len(resources)):
                        if str(new_labels[j][0]) in resources:
                            keylist_2 = resources[new_labels[j][0]].keys()
                            keylist_2.sort(reverse=True)
                            for key2 in keylist_2:
                                item2_v = resources[new_labels[j][0]][key2]
                    #             # print item1_v[0],item2_v[0]
                                # print new_labels[j][0]
                                for i2 in item2_v:
                                    if 'dbpedia' in i2[0]:
                                        try:
                                            link = urllib2.urlopen(i2[0])
                                            url2 = link.geturl()
                                            url2 = url2.replace('page','resource')
                                        except:
                                            url2 = i2[0]
                                    # print url2
                                    
                                    try:
                                        q1=('SELECT ?r WHERE  { <'+str(url1) + '> ?r <' +str(url2)+'>}')
                                        # print q1
                    #                     # if 'wikidata' in item1 and 'wikidata' in item2:
                    #                     #     print q1
                    #                     #     result1 = doSparqlQuery(q1)
                    #                     #     data = result1['results']['bindings'][0]
                    #                     #     print([str(item1),str(data['r']['value']),str(item2)])
                    #                     #     print '\n'
                    #                     #     rel =  data['r']['value'].split('/')
                    #                     #     relation.append(rel[-1])
                    #                     # if url1 not in my_item1 and url2 not in my_item2:
                                        if 'dbpedia' in url1 and 'dbpedia' in url2:
                                            # print "=url1"
                                            # print my_item1
                                            if url1 not in my_item1:
                                                result1 = sparql.query('http://dbpedia.org/sparql', q1)
                                                # print "urls============"
                                                # print url1
                                                print url2
                                                
                        #                         my_item2.append(url2)
                                                for row1 in result1:
                                                    values1 = sparql.unpack_row(row1)
                                                    if values1:
                                                        print "relations============"
                                                        print([str(url1),str(values1[0]),str(url2)])
                        #                                 print '\n'
                        #                                 rel =  values1[0].split('/')
                        #                                 relation.append(rel[-1])
                        #                         # print relation
                        #                                     # writer.writerow([str(item1),str(values1[0]),str(item2)])  
                        #                                 # relation.append(values1[0])
                                    except:
                                        pass
                            my_item1.append(url1) 

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
        # try:
        if row:
            doc = row
            tree = st.tag(doc.split())
            ent =  get_nodes_updated(tree)
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
            print ent
            resources = resource_extractor_updated(ent)
            print "====Resources===="
            print resources
            relation_extractor(resources)
            # print date_flag
            # now_current = datetime.datetime.now()
            # relation_extractor(resources)
            # total_time = datetime.datetime.now() - now_current
            # print total_time
            # if date_flag == 1:
            #     date_extractor(date,resources)
            #     date_flag = 0
            # objects.extend(ent)
        # except:
        #     pass