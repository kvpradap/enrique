from collections import OrderedDict
from magellan import DTMatcher
import magellan as mg

from magellan.gui.debug_gui_base import MainWindowManager
from magellan.debugmatcher.debug_gui_utils import *

def vis_debug_dt(matcher, train, test, exclude_attrs, target_attr):
    """
    Visual debugger for decision tree matcher

    Parameters
    ----------
    matcher : object, DTMatcher object
    train : MTable, containing training data with "True" labels
    test : MTable, containing test data with "True labels.
            The "True" labels are used for evaluation.
    exclude_attrs : List, attributes to be excluded from train and test,
        for training and testing.

    target_attr : String, column name in validation_set containing 'True' labels

    """

    assert set(test.columns) == set(train.columns), "The train and test columns are not same"
    assert set(train.columns).intersection(exclude_attrs) == set(exclude_attrs), "Some of exclude attrs are not part of" \
                                                                                 "train columns"
    # redundant
    assert set(test.columns).intersection(exclude_attrs) == set(exclude_attrs), "Some of exclude attrs are not part of" \
                                                                                "test columns"
    # fit using training data
    matcher.fit(table=train, exclude_attrs=exclude_attrs, target_attr=target_attr)
    predict_attr_name = get_name_for_predict_column(test.columns)
    predicted = matcher.predict(table=test, exclude_attrs=exclude_attrs, target_attr=predict_attr_name, append=True,
                                inplace=False)
    # print predicted
    eval_summary = mg.eval_matches(predicted, target_attr, predict_attr_name)
    # print eval_summary
    metric = get_metric(eval_summary)
    fp_dataframe = get_dataframe(predicted, eval_summary['false_pos_ls'])
    # print fp_dataframe.dtypes
    fn_dataframe = get_dataframe(predicted, eval_summary['false_neg_ls'])
    app = mg._viewapp
    m = MainWindowManager(matcher, "dt", exclude_attrs, metric, predicted, fp_dataframe, fn_dataframe)
    m.show()
    app.exec_()





def vis_tuple_debug_dt_matcher(matcher, t, exclude_attrs):
    if isinstance(matcher, DTMatcher):
        clf = matcher.clf
    else:
        clf = matcher
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
    # print feat_vals
    d = {}
    d.update(feat_vals)
    exec code in d
    # print code
    ret_val, node_list = d['debug_fn']()

    return ret_val, node_list