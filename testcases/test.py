# from pyparsing import Word, alphas, alphanums, Literal
# import magellan as mg
# attr_name = Word(alphanums +"_" + "." + "[" +"]" +'"')
# tok_fn = Word(alphanums+"_") + "(" + attr_name + ")"
# wo_tok = Word(alphanums) + "(" + attr_name + "," + attr_name + ")"
# wi_tok = Word(alphanums) + "(" + tok_fn + "," + tok_fn + ")"
# feat = wi_tok | wo_tok
# #t = feat.parseString('jaccard(qgm_3(ltuple.name), qgm_2(rtuple.name))')
# t = feat.parseString('jaccard(qgm_3(ltuple.name]), qgm_2(rtuple.name))')
# sim = mg.get_sim_funs()
# tok = mg.get_single_arg_tokenizers()
# print sim.keys()
# print tok.keys()
# tk = [ t not in tok for t in tok.keys()]
# print tk

import magellan as mg

A = mg.read_csv('../magellan/datasets/table_A.csv', key = 'ID')
B = mg.read_csv('../magellan/datasets/table_B.csv', key = 'ID')
feat_table = mg.get_features_for_blocking(A, B)
r = mg.get_feature_fn("jaccard(qgm_3(ltuple['address']), qgm_3(rtuple['address']))", mg._m_current_sim_funs,
                      mg._m_current_tokenizers)
print r
