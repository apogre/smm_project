# -*- coding: utf-8 -*- 

import nltk
from nltk.tree import *
import cPickle as pickle
import csv
import sys
from nltk.tag import StanfordNERTagger
from itertools import groupby
import re
import sparql
import psycopg2
from difflib import SequenceMatcher


objects = []
resources = {}

st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
conn = psycopg2.connect("dbname='smm_tweet' user='apradhan' host='localhost' password='wisepass'")
cur = conn.cursor()

def insert_data(res_tup):
    try:
        cur.executemany("""INSERT INTO entity(sent_id,entity_name,entity_type,resources) VALUES (%(sent_id)s, %(entity_name)s,%(entity_type)s, %(resources)s)""", res_tup)
    except:
        print "I am unable to connect to the database"


def similar_score(a,b):
    return SequenceMatcher(None,a,b).ratio()

def get_nodes_updated(netagged_words):
    ent = []
    for tag, chunk in groupby(netagged_words, lambda x:x[1]):
        if tag != "O":
            tuple1 =[" ".join(w for w, t in chunk),tag]
            ent.append(tuple1)
    return ent

def resource_extractor_updated(sent_id,labels):
    # print labels
    res_list = []
    for i,label in enumerate(labels):
        resources = {}
        value_list = []
        # print label
        resources["entity_name"] = label[0]
        resources["entity_type"] = label[1]
        resources["sent_id"] = sent_id+1
        # resource_list = []
        # score_list = {}
        q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . FILTER(regex(str(?label),"' +str(label[0]) +'", "i") && langMatches(lang(?label),"EN") )} limit 10')
        # print q_u
        try:
            result = sparql.query('http://localhost:8890/sparql', q_u)
            # # # print result
            # # types = {}
            for row in result:
                values = sparql.unpack_row(row)
                # print values[0]
                if not 'Category:' in values[0] and not 'wikidata' in values[0]:
                    # print values
                    score = similar_score(values[1],label[0])
                    if 'FC' in values[1] or 'F.C.' in values[1]:
                        score = score+1
                    values.append(score)
                    # print values
                    value_list.append(values)
            resources["resources"] = str(value_list)
        except:
            resources["resources"] = ""
        # print "======================"
        # print resources
        res_list.append(resources)
    return tuple(res_list)

# insert_data()
# sys.exit()
with open('tweet3.csv','rb') as csvfile:
    reader = csv.reader(csvfile)
    for i,row in enumerate(reader):
        print i
        doc = row[0]
        doc = doc.replace('RT','')
        try:
            tree = st.tag(doc.split())
            ent =  get_nodes_updated(tree)
            # print ent
            mentions = [[re.sub(r'\W+','',x),'mentions'] for x in doc.split() if x.startswith('@')]
            hashtags = [[re.sub(r'\W+','',x),'hashtags'] for x in doc.split() if x.startswith('#')]
            # print mentions
            mentions.extend(ent)
            mentions.extend(hashtags)
            # print mentions
            res_tup = resource_extractor_updated(i,mentions)
            # print res_tup
            insert_data(res_tup)
        except:
            with open('logs1.csv','ab') as csvf:
                swriter = csv.writer(csvf)
                swriter.writerow(row)
# cur.commit()
conn.commit()

# print entities
# with open('entity.txt','wb') as fp:
#     pickle.dump(objects,fp)