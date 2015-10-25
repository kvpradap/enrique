from collections import OrderedDict
from magellan import DTMatcher
import magellan as mg
import pandas as pd
import numpy as np
from magellan.gui.debug_gui_base import MainWindowManager

def vis_debug_dt(matcher, train, test, exclude_attrs, target_attr):
    assert set(test.columns) == set(train.columns), "The train and test columns are not same"
    assert set(train.columns).intersection(exclude_attrs) == set(exclude_attrs), "Some of exclude attrs are not part of" \
                                                                                 "train columns"
    # redundant
    assert set(test.columns).intersection(exclude_attrs) == set(exclude_attrs), "Some of exclude attrs are not part of" \
                                                                                "test columns"
    # fit using training data
    matcher.fit(table=train, exclude_attrs=exclude_attrs, target_attr=target_attr)
    predict_attr_name = _get_name_for_predict_column(test.columns)
    predicted = matcher.predict(table=test, exclude_attrs=exclude_attrs, target_attr=predict_attr_name, append=True,
                                inplace=False)
    eval_summary = mg.eval_matches(predicted, target_attr, predict_attr_name)
    metric = get_metric(eval_summary)
    fp_dataframe = get_dataframe(predicted, eval_summary['false_pos_ls'])
    print fp_dataframe.dtypes
    fn_dataframe = get_dataframe(predicted, eval_summary['false_neg_ls'])
    app = mg._viewapp
    m = MainWindowManager(matcher, "dt", exclude_attrs, metric, predicted, fp_dataframe, fn_dataframe)
    m.show()
    app.exec_()




def get_metric(summary_stats):
    d = OrderedDict()
    keys = summary_stats.keys()
    mkeys = [k for k in keys if k not in ['false_pos_ls', 'false_neg_ls']]
    for k in mkeys:
        d[k] = summary_stats[k]
    return d

def get_dataframe(table, ls):
    df = table.to_dataframe()
    ret = pd.DataFrame(columns=table.columns.values)
    if len(ls) > 0:
        l_fkey = table.get_property('foreign_key_ltable')
        r_fkey = table.get_property('foreign_key_rtable')
        df = df.set_index([l_fkey, r_fkey], drop=False)
        d = df.ix[ls]
        ret = d
        ret.reset_index(inplace=True, drop=True)
    return ret


def get_code_vis(tree, feature_names, target_names,
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

            # This code makes sense for printing the predicate
            # code_str = spacer + spacer_base + "print \'" + spacer_base + "" + features[node] + " <= " + str(
            #     threshold[node]) + \
            #            " is True " + "(  value : \'  + str(" + str(features[node]) + ") + \')\'"
            code_str = spacer + spacer_base + "node_list.append([True, \'" + str(features[node]) + " <= " + \
                       str(threshold[node]) + "\', " + str(features[node]) + "])"

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

            # code_str = spacer + spacer_base + "print \'" + spacer_base + "" + features[node] + " <= " + str(
            #     threshold[node]) + \
            #            " is False " + "(  value : \'  + str(" + str(features[node]) + ") + \')\'"

            code_str = spacer + spacer_base + "node_list.append([False, \'" + str(features[node]) + " <= " + \
                       str(threshold[node]) + "\', " + str(features[node]) + "])"

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
                code_str = spacer + "return " + str(target_name) + ", node_list" + \
                           " #( " + str(target_count) + " examples )"
                code_list.append(code_str)
                # print(spacer + "return " + str(target_name) + \
                #       " #( " + str(target_count) + " examples )")

    recurse(left, right, threshold, features, 0, 0)
    return code_list


def get_dbg_fn_vis(code):
    spacer_basic = '    '
    c = "def debug_fn(): \n"
    c += spacer_basic + "node_list = []\n"
    upd_code = [spacer_basic + e + "\n" for e in code]
    c = c + ''.join(upd_code)
    return c


def _get_name_for_predict_column(columns):
    k = '__predicted__'
    i = 0
    # try attribute name of the form "_id", "_id0", "_id1", ... and
    # return the first available name
    while True:
        if k not in columns:
            break
        else:
            k = '__predicted__' + str(i)
        i += 1
    return k

def vis_tuple_debug_dt_matcher(dt, t, exclude_attrs):
    if isinstance(dt, DTMatcher):
        clf = dt.clf
    else:
        clf = dt
    if isinstance(t, pd.Series):
        fv_columns = t.index
    else:
        fv_columns = t.columns
    if exclude_attrs is None:
        feature_names = fv_columns
    else:
        cols = [c not in exclude_attrs for c in fv_columns]
        feature_names = fv_columns[cols]

    code = get_code_vis(clf, feature_names, ['False', 'True'])
    code = get_dbg_fn_vis(code)
    feat_vals = OrderedDict(t.ix[t.index.values[0], feature_names])
    print feat_vals
    d = {}
    d.update(feat_vals)
    exec code in d
    # print code
    ret_val, node_list = d['debug_fn']()

    return ret_val, node_list