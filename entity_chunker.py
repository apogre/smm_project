import nltk
from nltk.tree import *
import cPickle as pickle

entities = []
ROOT = 'ROOT'
grammar = r"""
		NP: {<DT>?<JJ.*>*<NN.*>+}
			{}
	"""
cp = nltk.RegexpParser(grammar)

def ie_preprocess(doc):
	sentences = nltk.sent_tokenize(doc)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences] 
	return sentences

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
	            entities.extend(entity)
            else:
                pass
            getNodes(node)
        else:
        	pass



tagged = ie_preprocess(doc)
tree = cp.parse(tagged[0])

print tree

tree="(S (NP @/JJ GFFN/NNP)  :/:  (NP Crystal/JJ Palace/NNP)  and/CC  #/#  (NP LFc/NNP)  when/WRB  (NP Steve/NNP Mandanda/NNP)  plays/VBZ  ./.)"
tree = Tree.fromstring(tree)
getNodes(tree)

print entities
with open('entity.txt','wb') as fp:
	pickle.dump(entities,fp)