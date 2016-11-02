import cPickle as pickle

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
            q_u = ('SELECT distinct ?uri ?label WHERE { ?uri rdfs:label ?label . FILTER(regex(str(?label),"'+r'\\b' +str(label[0]) +r'\\b'+'", "i") && langMatches(lang(?label),"EN") )} limit 100')
            # print q_u
            result = sparql.query('http://dbpedia.org/sparql', q_u)
            # print result
            # types = {}
            for row in result:
                values = sparql.unpack_row(row)
                # print values
                if not 'Category:' in values[0] or 'alumni' in values[0]:
                    try:
                        q_type=('SELECT distinct ?type WHERE  { <'+str(values[0].encode('utf-8')) + '> rdf:type ?type }')
                        # print q_type
                        result_type = sparql.query('http://dbpedia.org/sparql', q_type)
                        type_list = []
                        for row_type in result_type:
                            types1 = sparql.unpack_row(row_type)
                            mytype =  types1[0].split('/')[-1]
                            types = str(mytype).translate(None,digits)
                            if '#' in types:
                                types = types.split('#')[-1]
                            type_list.append(types)
                        score = similar(values[1],label[0])
                        values.append(type_list)
                        if score in score_list:
                            score_list[score].append(values)
                        else:
                            score_list[score] = [values]
                        # resource_list.append(values[0])
                        # my_list = []
                        # q1=('SELECT distinct ?type ?superType WHERE  { <'+str(values[0]) + '> rdf:type ?type . optional { ?type rdfs:subClassOf ?superType } }')

                        # sys.exit()
                        #     my_list.append(values1)
                        # types[values[0]]= my_list
                    except:
                        pass
            # entities[i] = types
            q = ('select distinct ?x where{?x rdfs:label "'+ label[0] +'"@en }')
            result = sparql.query('http://dbpedia.org/sparql', q)
            for row in result:
                values = sparql.unpack_row(row)
                if not 'Category:' in values[0] or 'alumni' in values[0]:
                    # print values[0]
                    # resource_list.append(values[0])
                    q1=('SELECT distinct ?type WHERE  { <'+str(values[0].encode()) + '> rdf:type ?type }')
                    print q1
                    result1 = sparql.query('http://dbpedia.org/sparql', q1)
                    type_list = []
                    for row1 in result1:
                        values1 = sparql.unpack_row(row1)
                        mytype =  values1[0].split('/')[-1]
                        types = str(mytype).translate(None,digits)
                        if '#' in types:
                            types = types.split('#')[-1]
                        type_list.append(types)
                    main_value = [values[0],label[0],type_list]
                    if 1.0 in score_list:
                        score_list[1.0].append(main_value)
                    else:
                        score_list[1.0] = [main_value]
            resources[label[0]] = score_list
            # print resources
    # print types        
    return resources

entity_list = []

with open('entity_data.txt') as fp:
    data = pickle.load(fp)
    for d in data:
        print d
        if d not in entity_list:
            entity_list.append(d)

print entity_list, len(entity_list)

with open('entity_set.txt','wb') as fp:
  pickle.dump(entity_list,fp)