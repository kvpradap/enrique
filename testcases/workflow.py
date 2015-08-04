import magellan as mg

#i/o
A = mg.read_csv('../magellan/datasets/table_A.csv', key = 'ID')
B = mg.read_csv('../magellan/datasets/table_B.csv', key = 'ID')

mg.init_jvm()


# print A.properties
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
# print f.columns
st = 'jaccard(qgm_2(ltuple["address"]), qgm_2(rtuple["address"]))'
d = mg.get_feature_fn(st, s, t)
status = mg.add_feature(f, 'address_address_jac_qgm2_qgm2', d)
print f
print status
feat_table = mg.get_features_for_blocking(A, B)
print feat_table

