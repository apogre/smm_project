import sparql
import csv
import subprocess
import os
import requests
import json
import time
import sys
from nltk.tree import Tree
import os
# os.chdir('../stanford-corenlp-python/')
from corenlp import *
from difflib import SequenceMatcher



# e1 = select distinct ?c where{?x rdfs:label "Beckham"@en . }
# SELECT ?type ?superType WHERE 
# { 
#   # give me ?type of the resource
#   <http://dbpedia.org/resource/Thierry_Henry> rdf:type ?type .

#   # give me ?superTypes of ?type
#   OPTIONAL {
#    ?type rdfs:subClassOf ?superType .
#   }
# }

# os.chdir('../models/syntaxnet/')
# sentence = 'David Beckham and Victoria Beckham are married.'
# subprocess.call(['echo '+sentence +' | syntaxnet/demo.sh > output.txt'],shell=True)

#Using stanford nlp

sentence = 'The full name of Peru is Republic of Peru.'
# sentence = 'The capital of Peru is Lima.'
# sentence = 'The major languages in Peru are Spanish, Quechua and Aymara.'
# sentence = 'The population of Peru is 29.4 million.'

corenlp = StanfordCoreNLP()  # wait a few minutes...
parsed = corenlp.parse(sentence)
# parsed = '{"coref": [[[["Peru", 0, 8, 8, 9], ["Peru", 0, 4, 4, 5]]], [[["The full name of Peru", 0, 2, 0, 5], ["Republic of Peru", 0, 6, 6, 9]]]], "sentences": [{"parsetree": "(ROOT (S (NP (NP (DT The) (JJ full) (NN name)) (PP (IN of) (NP (NNP Peru)))) (VP (VBZ is) (NP (NP (NNP Republic)) (PP (IN of) (NP (NNP Peru))))) (. .)))", "text": "The full name of Peru is Republic of Peru.", "dependencies": [["root", "ROOT", "Republic"], ["det", "name", "The"], ["amod", "name", "full"], ["nsubj", "Republic", "name"], ["prep_of", "name", "Peru"], ["cop", "Republic", "is"], ["prep_of", "Republic", "Peru"]], "words": [["The", {"NamedEntityTag": "O", "CharacterOffsetEnd": "3", "Lemma": "the", "PartOfSpeech": "DT", "CharacterOffsetBegin": "0"}], ["full", {"NamedEntityTag": "O", "CharacterOffsetEnd": "8", "Lemma": "full", "PartOfSpeech": "JJ", "CharacterOffsetBegin": "4"}], ["name", {"NamedEntityTag": "O", "CharacterOffsetEnd": "13", "Lemma": "name", "PartOfSpeech": "NN", "CharacterOffsetBegin": "9"}], ["of", {"NamedEntityTag": "O", "CharacterOffsetEnd": "16", "Lemma": "of", "PartOfSpeech": "IN", "CharacterOffsetBegin": "14"}], ["Peru", {"NamedEntityTag": "LOCATION", "CharacterOffsetEnd": "21", "Lemma": "Peru", "PartOfSpeech": "NNP", "CharacterOffsetBegin": "17"}], ["is", {"NamedEntityTag": "O", "CharacterOffsetEnd": "24", "Lemma": "be", "PartOfSpeech": "VBZ", "CharacterOffsetBegin": "22"}], ["Republic", {"NamedEntityTag": "O", "CharacterOffsetEnd": "33", "Lemma": "Republic", "PartOfSpeech": "NNP", "CharacterOffsetBegin": "25"}], ["of", {"NamedEntityTag": "O", "CharacterOffsetEnd": "36", "Lemma": "of", "PartOfSpeech": "IN", "CharacterOffsetBegin": "34"}], ["Peru", {"NamedEntityTag": "LOCATION", "CharacterOffsetEnd": "41", "Lemma": "Peru", "PartOfSpeech": "NNP", "CharacterOffsetBegin": "37"}], [".", {"NamedEntityTag": "O", "CharacterOffsetEnd": "42", "Lemma": ".", "PartOfSpeech": ".", "CharacterOffsetBegin": "41"}]]}]}'
# print parsed
parsed = json.loads(parsed)

# sys.exit()
tree = parsed["sentences"][0]
words = tree["words"]
# print ptree
word = ''
prev_type = ''
mylabels = []
for w in words:
	if w[1]["PartOfSpeech"]=='NNP':
		if prev_type == 'NNP' or prev_type == 'IN':
			word = word+' '+w[0]
		else:
			prev_type = w[1]["PartOfSpeech"]
			word = w[0]
	elif w[1]["PartOfSpeech"] == 'IN':
		if prev_type =='NNP':
			word = word+ ' '+w[0]
	elif w[1]["PartOfSpeech"] == 'NN':
		predicate = w[0]
		prev_type=''
	else:
		prev_type=''
		if word:
			mylabels.append('"'+word+'"'+'@en')

print "sentence => "+sentence
filename='output.txt'

# sys.exit()
SPARQL_SERVICE_URL = 'https://query.wikidata.org/sparql'


def doSparqlQuery(query):
	r = requests.get(SPARQL_SERVICE_URL, params={'query': query, 'format': 'json'});
	return json.loads(r.text)

# def readata(filename):
#     file=open(filename,'r')
#     lines=file.readlines()
#     lines=lines[:-1]
#     data=csv.reader(lines,delimiter='\t')
#     lol=list(data)
#     return  lol

# lists=readata(filename)
# mylabels = []
# prev_type = ''
# for i,sublist in enumerate(lists):
# 	if sublist[4]=='NNP':
# 		if prev_type == 'NNP':
# 			word = word+' '+sublist[1]
# 		else:
# 			prev_type = sublist[4] 
# 			word = sublist[1]
# 	elif sublist[7]=='ROOT':
# 		predicate = sublist[1]
# 		prev_type=''
# 	else:
# 		prev_type=''
# 		mylabels.append('"'+word+'"'+'@en')

labels =  set(mylabels)
labels = list(labels)
print "predicate=>"+predicate
print labels

entities = {} 
resources = {}

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

json.dump(resources, open("resources1.txt",'w'))

relation=[]
# with open('mydata_type.csv','wb') as f:
# 	writer = csv.writer(f)

# resources = json.load(open("resources.txt"))

print "Relations"
print "========="
for item1 in resources[labels[0]]:
	for item2 in resources[labels[1]]:
		q1=('SELECT ?r WHERE  { <'+str(item1) + '> ?r <' +str(item2)+'>}')
		# print q1
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
						# writer.writerow([str(item1),str(values1[0]),str(item2)])	
					# relation.append(values1[0])
		except:
			pass

for item1 in resources[labels[0]]:
	q2=('SELECT ?r WHERE  { <'+str(item1) + '> ?r ' +str(labels[1])+' }')
	# print q2
	try:
		if 'wikidata' in item1:
			# print q2
			result1 = doSparqlQuery(q2)
			if result1:
				data = result1['results']['bindings'][0]
				print([str(item1),str(data['r']['value']),str(item2)])
				print '\n'
				rel =  data['r']['value'].split('/')
				relation.append(rel[-1])
		elif 'dbpedia' in item1:
			# print q2
			result1 = sparql.query('http://dbpedia.org/sparql', q2)
			for row1 in result1:
				values1 = sparql.unpack_row(row1)
				if values1:
					print([str(item1),str(values1[0]),str(labels[1])])
					print '\n'
					rel =  values1[0].split('/')
					relation.append(rel[-1])
					# writer.writerow([str(item1),str(values1[0]),str(item2)])	
				# relation.append(values1[0])
	except:
		pass

for item2 in resources[labels[1]]:
	q2=('SELECT ?r WHERE  { <'+str(item1) + '> ?r ' +str(labels[0])+' }')
	try:
		if 'wikidata' in item2:
			result1 = doSparqlQuery(q2)
			if result1:
				data = result1['results']['bindings'][0]
				print([str(item1),str(data['r']['value']),str(item2)])
				print '\n'
				rel =  data['r']['value'].split('/')
				relation.append(rel[-1])
		elif 'dbpedia' in item2:
			result1 = sparql.query('http://dbpedia.org/sparql', q2)
			for row1 in result1:
				values1 = sparql.unpack_row(row1)
				if values1:
					print([str(item1),str(values1[0]),str(labels[0])])
					print '\n'
					rel =  values1[0].split('/')
					relation.append(rel[-1])
					# writer.writerow([str(item1),str(values1[0]),str(item2)])	
				# relation.append(values1[0])
	except:
		pass

print "===================="
print sentence
print labels
print relation
print "predicate => " + predicate

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

for re in relation:
	if similar(re,predicate) > 0.6:
		print "The sentence is True"