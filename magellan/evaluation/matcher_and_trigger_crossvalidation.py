import magellan as mg
import numpy as np
import pandas as pd

from magellan.matcher.booleanrulematcher import BooleanRuleMatcher
from magellan.evaluation.evaluation import eval_matches
from magellan.debugmatcher.debug_gui_utils import get_name_for_predict_column
from sklearn.cross_validation import KFold
from sklearn import clone
from collections import OrderedDict
import pyprind

def cv_matcher_and_trigger(matcher, triggers, table, exclude_attrs,
                           target_attr, k=5, metric='precision', random_state=None):

    """
    Cross validate matcher and trigger.

    Parameters
    ----------
    matcher : object, An ML-object in Magellan
    triggers : List of MatchTrigger objects
    table : MTable, on which match + trigger should be done
    exclude_attrs : List of string, attribute names that should be excluded from training and evaluation
    target_attr : String, attribute name containing labels in the 'table'
    k : integer, specifies the number of folds for cross-validation. The default value is 5.
    metric : List of strings. Currently, the following values are allowed: 'precision', 'recall', 'f1',
        The list should form a subset of ['precision', 'recall', 'f1']. The default value is set to None.
        If None, then all the three metrics are computed for each fold and returned back to the user.
    random_state: int,Pseudo-random number generator state used for random sampling.
        If None, use default numpy RNG for shuffling
    :return:
    """

    metric = validate_and_get_metric_as_list(metric)

    folds = KFold(len(table), k, shuffle=True, random_state=random_state)
    table = table.copy()
    if isinstance(triggers, list) == False:
        triggers = [triggers]
    eval_ls = []
    ltable=table.get_property('ltable')
    rtable=table.get_property('rtable')
    foreign_key_ltable=table.get_property('foreign_key_ltable')
    foreign_key_rtable=table.get_property('foreign_key_rtable')
    if mg._progbar:
        bar = pyprind.ProgBar(k)
    for train_ind, test_ind in folds:
        train = mg.create_mtable(table.iloc[train_ind], key=table.get_key(),
                                     ltable=ltable,rtable=rtable,
                                     foreign_key_ltable=foreign_key_ltable,
                                     foreign_key_rtable=foreign_key_rtable)
        test = mg.create_mtable(table.iloc[test_ind], key=table.get_key(),
                                     ltable=ltable,rtable=rtable,
                                     foreign_key_ltable=foreign_key_ltable,
                                     foreign_key_rtable=foreign_key_rtable)
        if isinstance(matcher, BooleanRuleMatcher) == True:
            pred_col = get_name_for_predict_column(table.columns)
            predicted = matcher.predict(table=test, append=True, target_attr=pred_col,
                                        inplace=False)
        else:
            matcher.clf = clone(matcher.clf)
            matcher.fit(table=train, exclude_attrs=exclude_attrs,target_attr=target_attr)
            pred_col = get_name_for_predict_column(table.columns)
            predicted = matcher.predict(table=test, exclude_attrs=exclude_attrs,
                                        append=True, target_attr=pred_col, inplace=False)

        for t in triggers:
            t.execute(predicted, pred_col, inplace=True)

        eval_summary = eval_matches(predicted, target_attr, pred_col)
        eval_ls.append(eval_summary)
        if mg._progbar:
            bar.update()

    header = ['Metric', 'Num folds']
    fold_header = ['Fold ' + str(i+1) for i in range(k)]
    header.extend(fold_header)
    header.append('Mean score')
    dict_list = []

    for m in metric:
        d = get_metric_dict(eval_ls, k, m, header)
        dict_list.append(d)
    stats = pd.DataFrame(dict_list)
    stats = stats[header]
    res = OrderedDict()
    res['cv_stats'] = stats
    res['fold_stats'] = eval_ls
    return res

def validate_and_get_metric_as_list(metric):
    if metric is None:
        metric = ['precision', 'recall', 'f1']
    if isinstance(metric, list) == False:
        metric = [metric]
    validate_metric(metric)
    return metric


def validate_metric(metric):
    assert set(metric).issubset(['precision', 'recall', 'f1']) is True, "Metric should be a part of ['precision', " \
                                                                        "recall, 'f1'] "

def get_metric_dict(eval_ls, k, metric, header):

    val_list = [metric, k]
    scores = []
    for e in eval_ls:
        val_list.append(e[metric])
        scores.append(e[metric])
    mean_score = np.mean(scores)
    val_list.append(mean_score)

    d = OrderedDict(zip(header, val_list))
    return d
