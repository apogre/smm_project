import psycopg2
import sparql
from itertools import groupby
import operator
from difflib import SequenceMatcher
import sys
import re
import csv

conn = psycopg2.connect("dbname='smm_tweet' user='apradhan' host='localhost' password='wisepass'")
cur = conn.cursor()

ref = {"CPFC":"Crystal Palace","Gunners":"Arsenal","MCFC":"Manchester City","Reds":"Liverpool FC","United":"Manchester United","MUFC":"Manchester United","ManUtd":"Manchester United","EFC":"Everton FC","LFC":"Liverpool FC","NCFC":"New Castle FC","Blues":"Chelsea","CFC":"Chelsea","EPL":"English Premier","THFC":"Tottenham","premierleague":"premier league","Kop":"Liverpool FC","LCFC":"LeicesterCity","Foxes":"Leicester City"}

def redirect_link(o_link):
    try:
        link = urllib2.urlopen(o_link)
        url1 = link.geturl()
        r_link = url1.replace('page','resource')
    except:
        r_link = o_link
    return r_link

def similar(a,b):
    # print a, b
    try:
        raw_score = SequenceMatcher(None,a,b).ratio()
        # print raw_score
        if 'FC' in b.split() or 'F.C.' in b.split():
            raw_score = raw_score+1
        return raw_score
    except:
        return 0

def similar_loc(a,b):
    # print a, b
    try:
        raw_score = SequenceMatcher(None,a,b).ratio()
        return raw_score
    except:
        return 0

def resource_extractor_updated(ent):
    org_labels = ent[1].split()
    # org_labels = ["United"]
    if len(org_labels) == 1:
        if org_labels[0] in ref:
            new_labels = ref[org_labels[0]]
            my_labels = new_labels.split()
        else:
            my_labels = org_labels
    else:
        my_labels = org_labels
    # print ent
    try:
        if ent[2] == 'PERSON':
            if len(my_labels) == 1:
                q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . ?uri rdf:type foaf:Person . FILTER langMatches( lang(?label), "EN" ). ?label bif:contains "' +str(my_labels[0]) +'" . } ')
            else:
                q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . ?uri rdf:type foaf:Person . FILTER langMatches( lang(?label), "EN" ). ?label bif:contains "' +str(my_labels[-1]) +'" . FILTER (CONTAINS(?label, "'+str(my_labels[0])+'"))}')
        else:
            if len(my_labels) == 1:
                q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . FILTER langMatches( lang(?label), "EN" ). ?label bif:contains "' +str(my_labels[0]) +'" . }')
            else:
                q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label .  FILTER langMatches( lang(?label), "EN" ). ?label bif:contains "' +str(my_labels[1]) +'" . FILTER (CONTAINS(?label, "'+str(my_labels[0])+'"))}')
    
        # print q_u
        # sys.exit()
        result = sparql.query('http://dbpedia.org/sparql', q_u)
        values = [sparql.unpack_row(row) for row in result]
        if values:
            new_val = [redirect_link(val) for val in values if not 'Category:' in val[0] and not 'wikidata' in val[0]]
            # print new_val
            values = new_val
            # print values
            # print ent[1]
            # for val in values:
            #     test = similar(ent[1],val[1])
            #     print test,val[1]
            if ent[2] == 'LOCATION':
                add_score = [similar_loc(ent[1],val[1]) for val in values]
            else:
                add_score = [similar(ent[1],val[1]) for val in values]
            # print add_score
            for s,score in enumerate(add_score):
                values[s].append(score)
            sorted_values = sorted(values,key=operator.itemgetter(2),reverse=True)
            # print ent[0],sorted_values[1:10]
            if sorted_values:
            #     # print row[0], str(sorted_values[1:10])
                u_q = """UPDATE entity set resources = %s where id = %s"""
                # print u_q
                cur.execute(u_q,('"'+str(sorted_values[1:10])+'"',ent[0]))
                conn.commit()
            else:
                pass
    except:
        # print 'no value'
        with open('entity_resource.csv','ab') as csvf:
            swriter = csv.writer(csvf)
            swriter.writerow(ent)
            # pass


cur.execute("SELECT id,entity_name,entity_type from entity where resources = '' and id > 14007")
entities = cur.fetchall()
for ent in entities:
    print ent[0]
    # ent[1]='United'
    resource_extractor_updated(ent)

print "Operation done successfully";
conn.close()