from nltk.tree import *
import cPickle as pickle
import csv
import nltk

entities = []
ROOT = 'ROOT'
def getNodes(parent):
    for node in parent:
        if type(node) is Tree:
            if node.label() == ROOT:
                print "======== Sentence ========="
                print "Sentence:", " ".join(node.leaves())
            elif node.label() == 'ORGANIZATION' or node.label() =='PERSON' or node.label() =='LOCATION' or node.label() =='FACILITY' or node.label() =='GPE':
	            # print '==>',node.label(), node.leaves()
	            entity = node.leaves()
	            entity = ' '.join(e.split('/')[0] for e in entity)
	            if '@' in entity:
	            	entity = ''.join(entity.split(' '))
	            print entity
	            entities.append(entity)
            else:
                # pass
                print '==>',node.label(), node.leaves()
            getNodes(node)
        else:
        	pass
            # print "Word:", node

# with open('tweet3.csv','rb') as csvfile:
#     reader = csv.reader(csvfile)
#     for row in reader:
#         print row[0]

tree="(S  @/JJ GFFN/NNP :/: (ORGANIZATION Crystal/JJ Palace/NNP) when/WRB (PERSON Steve/NNP Mandanda/NNP) plays:6/NN matches/NNS ,/, 0/CD losses/NNS  ./.)"
tree = Tree.fromstring(tree)
# sent = "Crystal Palace went to Liverpool."
# print nltk.ne_chunk(sent)
getNodes(tree)

# print entities
# with open('entity.txt','wb') as fp:
# 	pickle.dump(entities,fp)