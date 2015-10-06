import sys
import magellan as mg
import pandas as pd
import numpy as np
import os
import subprocess
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from magellan.feature.extractfeatures import apply_feat_fns


# ------------------ functions --------------------------------------------


def visualize_tree(tree, feature_names):
    """Create tree png using graphviz.

    Args
    ----
    tree -- scikit-learn DecsisionTree.
    feature_names -- list of feature names.
    """
    with open("dt.dot", 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names)

    #command = ["dot", "-Tpng", "dt.dot", "-o", "dt.png"]
    # #try:
    #     subprocess.check_call(command)
    # except:
    #     exit("Could not run dot, ie graphviz, to "
    #          "produce visualization")


def get_code(tree, feature_names, target_names,
             spacer_base="    "):
    """Produce psuedo-code for decision tree.

    Args
    ----
    tree -- scikit-leant DescisionTree.
    feature_names -- list of feature names.
    target_names -- list of target (class) names.
    spacer_base -- used for spacing code (default: "    ").

    Notes
    -----
    based on http://stackoverflow.com/a/30104792.
    """
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value

    code_list = []

    def recurse(left, right, threshold, features, node, depth):
        spacer = spacer_base * depth
        if (threshold[node] != -2):
            code_str = spacer + "if ( " + features[node] + " <= " + \
                       str(threshold[node]) + " ):"
            code_list.append(code_str)
            # print(spacer + "if ( " + features[node] + " <= " + \
            #       str(threshold[node]) + " ):")

            code_str = spacer + spacer_base + "print \'" + spacer + "Condition " + features[node] + " <= " + str(
                threshold[node]) + \
                       " PASSED " + "(  value : \'  + str(" + str(features[node]) + ") + \')\'"
            code_list.append(code_str)

            # print(spacer + spacer_base + "print \'" + features[node] + " <= " + str(threshold[node]) +
            #       " PASSED " + "(  value : \'  + str(" +  str(features[node])  + ") + \')\'")
            if left[node] != -1:
                recurse(left, right, threshold, features,
                        left[node], depth + 1)
            # print(spacer + "}\n" + spacer +"else:")
            code_str = spacer + "else:"
            code_list.append(code_str)
            # print(spacer + "else:")


            code_str = spacer + spacer_base + "print \'" + spacer + "Condition " + features[node] + " <= " + str(
                threshold[node]) + \
                       " FAILED " + "(  value : \'  + str(" + str(features[node]) + ") + \')\'"
            code_list.append(code_str)
            # print(spacer + spacer_base + "print \'" + features[node] + " <= " + str(threshold[node]) +
            #       " FAILED " + "(  value : \'  + str(" +  str(features[node])  + ") + \')\'")


            if right[node] != -1:
                recurse(left, right, threshold, features,
                        right[node], depth + 1)
                # print(spacer + "}")
        else:
            target = value[node]
            for i, v in zip(np.nonzero(target)[1],
                            target[np.nonzero(target)]):
                target_name = target_names[i]
                target_count = int(v)
                # print(spacer + "return " + str(target_name) + \
                #       " ( " + str(target_count) + " examples )")
                code_str = spacer + "return " + str(target_name) + \
                           " #( " + str(target_count) + " examples )"
                code_list.append(code_str)
                # print(spacer + "return " + str(target_name) + \
                #       " #( " + str(target_count) + " examples )")

    recurse(left, right, threshold, features, 0, 0)
    return code_list


def debug_dt(t1, t2, feat_table, clf):
    code = get_code(dt.clf, list(feat_table['feature_name']), ['False', 'True'])
    feat_vals = apply_feat_fns(t1, t2, feat_table)
    code = get_dbg_fn(code)
    # print code
    d = {}
    d.update(feat_vals)
    exec code in d
    ret_val = d['debug_fn']()
    print "Tuples match status : " + str(ret_val)


def get_dbg_fn(code):
    spacer_basic = '    '
    c = "def debug_fn(): \n"
    upd_code = [spacer_basic + e + "\n" for e in code]
    c = c + ''.join(upd_code)
    return c


# -------------------- main ------------------------------------------------

# A = mg.load_dataset('table_A')
# B = mg.load_dataset('table_B')
# feat_table = mg.get_features_for_blocking(A, B)
# mg.init_jvm('C:\\Program Files\\Java\\jre7\\bin\\server\\jvm.dll')
# ab = mg.AttrEquivalenceBlocker()
# C = ab.block_tables(A, B, 'zipcode', 'zipcode', l_output_attrs=['name', 'hourly_wage', 'zipcode'],
#                     r_output_attrs=['name', 'hourly_wage', 'zipcode'])
# x = [10, 13, 16, 20]
# feat_table = feat_table.ix[x]
# S = mg.sample_one_table(C, 10)
#
# L = mg.load_table('label.pkl')
# L.set_property('ltable', A)
# L.set_property('rtable', B)
#
# S_prime = mg.extract_feat_vecs(L, attrs_after='label', feat_table=feat_table)
# dt = mg.DTMatcher(random_state=42)
# dt.fit(table=S_prime, exclude_attrs=['_id', 'ltable.ID', 'rtable.ID'], target_attr='label')
#
# debug_dt(A.ix[1], B.ix[2], feat_table, dt.clf)

# code = get_code(dt.clf, list(feat_table['feature_name']), ['False', 'True'])
# d = {}
# d['hourly_wage_hourly_wage_exm'] = 1.0
#
# #
# c = ""
# spacer_basic = '    '
# c = "def debug_fn(): \n"
# upd_code = [spacer_basic + e + "\n" for e in code]
#
# c = c + ''.join(upd_code)
# exec c in d
# print c
# d['debug_fn']()
#
# t1 = A.ix[1]
# t2 = B.ix[2]
# feat_vals = apply_feat_fns(t1, t2, feat_table)
# print feat_vals
# exec c in feat_vals
# print feat_vals['debug_fn']()
#
# #print code



# ---------------- books
# coding: utf-8

# In[1]:

import sys

sys.path.append('C:/Pradap/Research/Python-Packages/enrique')

wal = mg.read_csv('../magellan/datasets/books/walmart.csv',
                  dtype={'isbn': pd.np.str, 'pages': pd.np.str, 'volume': pd.np.str, 'editionNum': pd.np.str},
                  low_memory=False, key='id')

bwk = mg.read_csv('../magellan/datasets/books/bowker.csv',
                  dtype={'isbn': pd.np.str, 'pages': pd.np.str, 'volume': pd.np.str, 'editionNum': pd.np.str},
                  low_memory=False, key='id')

ab = mg.AttrEquivalenceBlocker()
candset = ab.block_tables(bwk, wal, 'isbn', 'isbn', ['title', 'author'], ['title', 'author'])

feat_table = mg.get_features_for_blocking(bwk, wal)

sample_cset = mg.sample_table(candset, 30)

mg.init_jvm('C:\\Program Files\\Java\\jre7\\bin\\server\\jvm.dll')

from magellan.feature.simfunctions import lev


# label_cset = mg.label(sample_cset, "gold_label")
# label_cset.save_table('book_label.pkl')
label_cset = mg.load_table('book_label.pkl')
label_cset.set_property('ltable', bwk)
label_cset.set_property('rtable', wal)

fv = mg.extract_feat_vecs(label_cset, feat_table=feat_table, attrs_after=['gold_label'])

dt = mg.DTMatcher(random_state=81)
dt.fit(table=fv, exclude_attrs=['_id', 'ltable.id', 'rtable.id', 'gold_label'], target_attr='gold_label')
cols = [c not in ['_id', 'ltable.id', 'rtable.id', 'gold_label'] for c in fv.columns]
feature_names = fv.columns[cols]
visualize_tree(dt.clf, feature_names)
# debug_dt(wal.ix[2], bwk.ix[3], feat_table, dt.clf)
t1 = wal.ix[3]
t2 = bwk.ix[3]

f = apply_feat_fns(t1, t2, feat_table)
# print dt.predict(f)
debug_dt(wal.ix[3], bwk.ix[3], feat_table, dt.clf)
print "Hi"
