from magellan import RFMatcher
import magellan as mg
from magellan.gui.debug_gui_base import MainWindowManager
from magellan.debugmatcher.debug_gui_utils import *
from magellan.debugmatcher.debug_gui_decisiontree_matcher import vis_tuple_debug_dt_matcher

def vis_debug_rf(matcher, train, test, exclude_attrs, target_attr):
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
    eval_summary = mg.eval_matches(predicted, target_attr, predict_attr_name)
    metric = get_metric(eval_summary)
    fp_dataframe = get_dataframe(predicted, eval_summary['false_pos_ls'])
    fn_dataframe = get_dataframe(predicted, eval_summary['false_neg_ls'])
    app = mg._viewapp
    m = MainWindowManager(matcher, "rf", exclude_attrs, metric, predicted, fp_dataframe, fn_dataframe)
    m.show()
    app.exec_()

def vis_tuple_debug_rf_matcher(matcher, t, exclude_attrs):
    if isinstance(matcher, RFMatcher):
        clf = matcher.clf
    else:
        clf = matcher
    # if isinstance(t, pd.Series):
    #     fv_columns = t.index
    # else:
    #     fv_columns = t.columns
    # if exclude_attrs is None:
    #     feature_names = fv_columns
    # else:
    #     cols = [c not in exclude_attrs for c in fv_columns]
    #     feature_names = fv_columns[cols]
    consol_node_list = []
    consol_status = []

    for e in clf.estimators_:
        # print t
        ret_val, node_list = vis_tuple_debug_dt_matcher(e, t, exclude_attrs)
        consol_status.append(ret_val)
        consol_node_list.append([ret_val, node_list])
    ret_val = False
    prob_true = float(sum(consol_status))/len(clf.estimators_)
    prob_false = 1 - prob_true
    if prob_true > prob_false:
        ret_val = True
    return ret_val, consol_node_list





