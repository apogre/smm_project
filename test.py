import cPickle as pickle

with open('entity.txt','rb') as fp:
	data = pickle.load(fp)

print data