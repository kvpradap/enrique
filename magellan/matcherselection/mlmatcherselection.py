from magellan import diff
import numpy as np

from collections import OrderedDict
from sklearn.cross_validation import KFold, cross_val_score
from sklearn.preprocessing import Imputer


def select_matcher(matchers, x=None, y=None, table=None, exclude_attrs=None, target_attr=None,
                   metric='precision', k=5):
    """
    Select matcher using cross validation

    Parameters
    ----------
    matchers : list, of matcher objects
    x : MTable, defaults to None
        of feature vectors (as of now it is a data frame)

    y : MTable, defaults to None
        of labels (as of now it is a data frame)

    table : MTable, defaults to None,
        of feature vectors and user included attributes

    exclude_attrs : list,
        list of user attributes to be excluded from table (foreign keys and keys are automatically removed*)

    target_attr : string,
        target attribute name containing gold labels

    metric = string, should be one of the following 'precision', 'recall', 'f1', 'accuracy'
    k : integer,
        number of folds to be used in cross validation

    Returns
    -------
    result : dict* need to update it
    """
    x, y, xy_flag = get_data_in_xy_format(x, y, table, exclude_attrs, target_attr)
    # @todo: do imputation as of now (SHOULD REMOVE LATER) -- start
    imp = Imputer(missing_values='NaN', strategy='median', axis=0)
    imp.fit(x)
    # replace nan in imputer to 0
    imp.statistics_[np.isnan(imp.statistics_)] = 0.0
    x = imp.transform(x)

    # check "matchers" is a list, if not convert it into a list
    if not isinstance(matchers, list):
        matchers = [matchers]
    # get cv results for each matcher
    matcher_index = 0
    matcher_eval_results = OrderedDict()
    matcher_eval_summary = []
    for matcher in matchers:

        matcher_cv_results = cross_validation(matcher, x, y, k)
        matcher_cv_results = update_cv_results_with_summary(matcher_cv_results)

        # get evaluation summary for each matcher that be displayed back to the user
        eval_summary = get_matcher_result_summary(matcher, matcher_index, matcher_cv_results)
        matcher_eval_summary.append(eval_summary)

        matcher_eval_results[matcher_index] = matcher_cv_results
        matcher_index += 1

    # get the best matcher based on the metric


    pass


def get_data_in_xy_format(x, y, table, exclude_attrs, target_attr):
    xy_flag = False
    if x is not None and y is not None:
        xy_flag = True
        x, y = get_data_in_xy_format_given_projection(x, y)
        return x, y, xy_flag
    elif table is not None and exclude_attrs is not None and target_attr is not None:
        x, y = get_data_in_xy_format_given_ex_attrs(table, exclude_attrs, target_attr)
        return x, y, xy_flag
    else:
        raise SyntaxError('The arguments supplied does not match with the signatures supported')

def get_data_in_xy_format_given_projection(x, y):
    x = x.values
    y = y.values
    return x, y

def get_data_in_xy_format_given_ex_attrs(table, exclude_attrs, target_attr):
    if not isinstance(exclude_attrs, list):
        exclude_attrs = [exclude_attrs]
    # get a set with key and foreign keys
    s = set([table.get_key(), table.get_property('foreign_key_ltable'), table.get_property('foreign_key_rtable')])
    exclude_attrs = list(set(exclude_attrs).union(s))
    attrs_to_project = diff(table.columns, exclude_attrs)
    x = table[attrs_to_project].values
    y = table[target_attr].values
    return x, y


def cross_validation(matcher, x, y, k):
    #should return a dict with the following information
    # n_tp, n_tn, n_fp, n_fn, 'precision', 'recall', 'f1', 'accuracy', fn_list, fp_list
    kf = KFold(len(y), k, shuffle=True, random_state=0)
    matcher_cv_results = dict()
    fold_index = 0
    for train, test in kf:
        clf = matcher.clf.copy()
        clf.fit(x[train], y[train])
        gold = y[test]
        predicted = clf.predict(x[test])
        result = get_all_metrics(predicted, gold)
        matcher_cv_results[fold_index] = result
        fold_index += 1
    return matcher_cv_results

def update_cv_results_with_summary(cv_results):
    prec_list = []
    recall_list = []
    f1_list = []
    acc_list = []
    union_fp_indices = []
    union_fn_indices = []
    union_tp_indices = []
    union_tn_indices = []

    for result in cv_results:
        prec_list.append(result['precision'])
        recall_list.append(result['recall'])
        f1_list.append(result['f1'])
        acc_list.append(result['accuracy'])
        # Caution: each fold stores indices as list, so make sure to "extend" it
        union_fp_indices.extend(result['false_pos_indices'])
        union_fn_indices.extend(result['false_neg_indices'])
        union_tn_indices.extend(result['true_neg_indices'])
        union_tp_indices.extend(result['true_pos_indices'])
    cv_results['mean_precision'] = np.mean(prec_list)
    cv_results['mean_recall'] = np.mean(recall_list)
    cv_results['mean_f1'] = np.mean(f1_list)
    cv_results['mean_accuracy'] = np.mean(acc_list)
    cv_results['union_false_pos_indices'] = list(set(union_fp_indices))
    cv_results['union_false_neg_indices'] = list(set(union_fn_indices))
    cv_results['union_true_pos_indices'] = list(set(union_tp_indices))
    cv_results['union_true_neg_indices'] = list(set(union_tn_indices))
    return cv_results


def get_all_metrics(predicted, gold):

    # get false label indices
    gf = np.nonzero(gold == 0)[0]
    pf = np.nonzero(predicted == 0)[0]

    # get true label indices
    gt = np.nonzero(gold == 1)[0]
    pt = np.nonzero(predicted == 1)[0]

    # get false postive indices
    fp_indices = list(set(gf).intersection(pt))

    # get true_positve indices
    tp_indices = list(set(gt).intersection(pt))

    # get false negative indices
    fn_indices = list(set(gt).intersection(pf))

    # get true negative indices
    tn_indices = list(set(gf).intersection(pf))

    n_tp = float(len(tp_indices))
    n_fp = float(len(fp_indices))
    n_fn = float(len(fn_indices))
    n_tn = float(len(tn_indices))
    prec_num = n_tp
    prec_den = n_tp + n_fp
    rec_num = n_tp
    rec_den = n_tp + n_fn
    precision = prec_num/prec_den
    recall = rec_num/rec_den
    acc_num = (n_tp + n_tn)
    acc_den = len(gold)
    accuracy = acc_num/acc_den
    if precision == 0.0 and recall == 0.0:
        f1 = 0.0
    else:
        f1 = (2.0*precision*recall)/(precision + recall)

    result = OrderedDict()
    result['prec_numerator'] = prec_num
    result['prec_denominator'] = prec_den
    result['precision'] = precision
    result['recall_numerator'] = rec_num
    result['recall_denominator'] = rec_den
    result['recall'] = recall
    result['f1'] = f1
    result['acc_numerator'] = acc_num
    result['acc_denominator'] = acc_den
    result['accuracy'] = accuracy
    result['false_pos_num'] = n_fp
    result['false_pos_indices'] = fp_indices
    result['false_neg_num'] = n_fn
    result['false_neg_indices'] = fn_indices
    result['true_pos_num'] = n_tp
    result['true_pos_indices'] = tp_indices
    result['true_neg_num'] = n_tn
    result['true_neg_indices'] = tn_indices

    return result

def get_matcher_result_summary(matcher, matcher_index, result):
    d = OrderedDict()
    d['matcher_name'] = matcher.name
    d['matcher_index'] = matcher_index
    d['mean_precision'] = result['mean_precision']
    d['mean_recall'] = result['mean_recall']
    d['mean_f1'] = result['mean_f1']
    d['mean_accuracy'] = result['mean_accuracy']
    d['matcher_object'] = matcher
    return d