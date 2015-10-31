from magellan.evaluation.matcher_and_trigger_crossvalidation import cv_matcher_and_trigger
import magellan as mg
import pandas as pd

mg.init_jvm()
# Read walmart books data
wal =  mg.read_csv(mg.get_install_path()+'/datasets/books/walmart.csv',
                    dtype={'isbn':pd.np.str, 'pages':pd.np.str, 'volume':pd.np.str, 'editionNum':pd.np.str},
                    low_memory=False, key='id')
# Read bowker books data
bwk = mg.read_csv(mg.get_install_path()+'/datasets/books/bowker.csv',
                  dtype={'isbn':pd.np.str, 'pages':pd.np.str, 'volume':pd.np.str, 'editionNum':pd.np.str},
                  low_memory=False, key='id')

L = mg.read_csv('label_ab_correct_books.csv', ltable=wal, rtable=bwk)
feature_table = mg.get_features_for_matching(wal, bwk)
f = feature_table.ix[[3,7,18,26, 53]]
m = mg.DTMatcher()


# feature_table = mg.get_features_for_matching(A, B)
G = mg.extract_feat_vecs(L, feature_table=f, attrs_after='gold')
G = mg.impute_table(G, exclude_attrs=['_id', 'ltable.id', 'rtable.id', 'gold'], strategy='most_frequent')
# m = mg.LinRegMatcher()
# print G
pos_trigger = mg.MatchTrigger()
pos_trigger.add_cond_rule('author_author_lev(ltuple, rtuple) == 1',
                          feature_table=feature_table)
pos_trigger.add_cond_status(True)
pos_trigger.add_action(1)

neg_trigger = mg.MatchTrigger()
neg_trigger.add_cond_rule(['lang_lang_lev(ltuple, rtuple) > 0.5'],
    feature_table=feature_table)
neg_trigger.add_cond_status(False)
neg_trigger.add_action(0)

t = cv_matcher_and_trigger(m, [pos_trigger],  table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
                           target_attr='gold', k=5, metric='precision', random_state=1)
# Create rule-based matcher and add rules.
# rm = mg.BooleanRuleMatcher()
# rm.add_rule(['title_title_jac_qgm_3_qgm_3(ltuple, rtuple) > 0.6'
#              ],
#             feature_table=feature_table)
# rm.add_rule(['author_author_jac_qgm_3_qgm_3(ltuple, rtuple) > 0.6'],
#             feature_table=f)
# rm.add_rule(['binding_binding_jac_qgm_3_qgm_3(ltuple, rtuple) > 0.5'],
#             feature_table=f)
#
# X = rm.predict(table=L, target_attr='predicted',
#                append=True, inplace=False)
# eval_summary = mg.eval_matches(X, 'gold', 'predicted')

# q = cv_matcher_and_trigger(rm, [neg_trigger],  table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
#                            target_attr='gold', k=5, metric='precision', random_state=1)
# print eval_summary

print t['cv_stats']

# t = cv_matcher_and_trigger(m, [neg_trigger],  table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
#                            target_attr='gold', k=5, metric='precision', random_state=1)
#
# # print t['cv_stats']
#
# t = cv_matcher_and_trigger(m, [pos_trigger, neg_trigger],  table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
#                            target_attr='gold', k=5, metric='precision', random_state=1)
# print t['cv_stats']

# res = mg.select_matcher([m], table=G, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID', 'gold'],
#                            target_attr='gold', k=5, metric='precision', random_state=0)
# print res['cv_stats']
