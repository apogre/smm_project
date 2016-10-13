from nltk.tree import *
import cPickle as pickle

entities = []
ROOT = 'ROOT'
def getNodes(parent):
    for node in parent:
        if type(node) is Tree:
            if node.label() == ROOT:
                print "======== Sentence ========="
                print "Sentence:", " ".join(node.leaves())
            elif node.label() == 'NP':
	            # print '==>',node.label(), node.leaves()
	            entity = node.leaves()
	            entity = ' '.join(e.split('/')[0] for e in entity)
	            if '@' in entity:
	            	entity = ''.join(entity.split(' '))
	            print entity
	            entities.append(entity)
            else:
                pass
            getNodes(node)
        else:
        	pass
            # print "Word:", node

tree="(S (NP @/JJ GFFN/NNP)  :/:  (NP Crystal/JJ Palace/NNP)  and/CC  #/#  (NP LFc/NNP)  when/WRB  (NP Steve/NNP Mandanda/NNP)  plays/VBZ  ./.)"
tree = Tree.fromstring(tree)
getNodes(tree)

print entities
with open('entity.txt','wb') as fp:
	pickle.dump(entities,fp)