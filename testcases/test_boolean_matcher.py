import magellan as mg
import pandas as pd
mg.init_jvm()
A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')
sim = mg.get_sim_funs()
tok = mg.get_single_arg_tokenizers()
address_feature = mg.get_feature_fn("jaccard(qgm_3(ltuple['address']), qgm_3(rtuple['address']))", sim, tok)
name_feature = mg.get_feature_fn("lev(ltuple['name'], rtuple['name'])", sim , tok)
hourly_feature = mg.get_feature_fn("abs_norm(ltuple['hourly_wage'], rtuple['hourly_wage'])", sim, tok)
# rules


feat_table = pd.DataFrame(columns=['feature_name', 'left_attribute', 'right_attribute', 'left_attr_tokenizer',
                              'right_attr_tokenizer', 'simfunction', 'function', 'function_source'])
mg.add_feature(feat_table,  'address_address_jac_qgm_3_qgm_3', address_feature)
mg.add_feature(feat_table, 'name_name_lev', name_feature)
mg.add_feature(feat_table, 'hourly_wage_abs_norm', hourly_feature)

# block using zipcode
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', l_output_attrs=['name', 'address', 'hourly_wage'],
                    r_output_attrs=['name', 'address', 'hourly_wage'])

# get_features

F = mg.extract_feat_vecs(C, attrs_before=['ltable.name', 'rtable.name', 'ltable.address', 'rtable.address',
                                          'ltable.hourly_wage', 'rtable.hourly_wage'],
                                          feat_table=feat_table)
mg.view(F)
# matcher
bm = mg.BooleanRuleMatcher()
bm.add_rule(['address_address_jac_qgm_3_qgm_3(ltuple, rtuple) > 0.9', 'name_name_lev(ltuple, rtuple) > 0.6'], feat_table)
bm.add_rule(['hourly_wage_abs_norm(ltuple, rtuple) > 0.99'], feat_table)
E = bm.predict(F, 'label', append=True)
mg.view(F)
print F
