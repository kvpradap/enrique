import magellan as mg

#i/o
A = mg.read_csv('../magellan/datasets/table_A.csv', key = 'ID')
B = mg.read_csv('../magellan/datasets/table_B.csv', key = 'ID')

mg.init_jvm('C:\\Program Files\\Java\\jre7\\bin\\server\\jvm.dll')
#mg.init_jvm()

ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', l_output_attrs=['name', 'hourly_wage'],
                    r_output_attrs=['name', 'hourly_wage'])
# print C
# print C.properties
# print "----------------"

E = ab.block_tables(A, B, 'hourly_wage', 'hourly_wage', l_output_attrs=['birth_year']
                   )
# print E
# print "----------------"
D = ab.block_candset(C, 'birth_year', 'birth_year')
# print D
# print D.properties
# print "----------------"

F = mg.combine_block_outputs_via_union([D, E])
#print F.properties
#print F
#print "----------------"

S = mg.sample_one_table(C, 13)
#print S.get_key()
#print S.get_property('foreign_key_ltable')
#print S

L = mg.label(S, 'gold_label')
#print L
#print L.properties

#
# A.to_csv('./table_a_test.csv', index=False)
# A.save_table('./table_a.pkl')
#
# A1 = mg.load_table('./table_a.pkl')
# print type(A1)
# #print A1.properties
#
# A1 = mg.sample_one_table(A, 4)
# #print A1
# #print A1.properties
# A1, B1 = mg.sample_two_tables(A, B, 4, 2)
# print A1
#
# print B1


s = mg.get_sim_funs()
t = mg.get_single_arg_tokenizers()
t_A = mg.get_attr_types(A)
t_B = mg.get_attr_types(B)
c = mg.get_attr_corres(A, B)
f = mg.get_features(A, B, t_A, t_B, c, t, s)
# # print f.columns
# st = 'jaccard(qgm_2(ltuple["address"]), qgm_2(rtuple["address"]))'
# d = mg.get_feature_fn(st, s, t)
# status = mg.add_feature(f, 'address_address_jac_qgm2_qgm2', d)
# print f
# print status
# feat_table = mg.get_features_for_blocking(A, B)
# print feat_table
print L.columns
s_prime = mg.extract_feat_vecs(L, attrs_before=None, feat_table=f, attrs_after=['gold_label'])
print s_prime
nb = mg.NBMatcher()
#nb.fit(table=s_prime, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold_label'], target_attr='gold_label')
#nb.fit(x=s_prime[list(f['feature_name'])], y=s_prime['gold_label'])
c_prime = mg.extract_feat_vecs(F, feat_table=f)
#y = nb.predict(table=c_prime, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'ltable.birth_year'],
#               target_attr='predicted_label', append=True)

#y = nb.predict(x = c_prime[list(f['feature_name'])])

dt = mg.DTMatcher()
rf = mg.RFMatcher()

m = mg.select_matcher([nb, dt, rf], x=s_prime[list(f['feature_name'])], y=s_prime['gold_label'], k=5 )
print m
mc = mg.selector_matcher_combiner([nb, dt, rf], ['majority'], x=s_prime[list(f['feature_name'])], y=s_prime['gold_label'], k=5)
print mc


