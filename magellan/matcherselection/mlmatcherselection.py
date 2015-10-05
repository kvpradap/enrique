from magellan import diff
import numpy as np

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
    # --- end




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
    for train, test in kf:
        clf = matcher.clf.copy()
        clf.fit(x[train], y[train])
        # need to complete ....
    pass



