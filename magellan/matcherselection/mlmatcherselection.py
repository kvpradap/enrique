import magellan as mg
import numpy as np
import pandas as pd

from sklearn.cross_validation import KFold, cross_val_score
from sklearn.preprocessing import Imputer

from collections import OrderedDict

def select_matcher(matchers, x=None, y=None, table=None, exclude_attrs=None, target_attr=None, metric='precision', k=5):
    """
    Select matcher using cross validation

    Parameters
    ----------
    matchers : list, of matcher objects
    x : MTable, defaults to None
        of feature vectors
    y : MTable, defaults to None
        of labels
    table : MTable, defaults to None
            of feature vectors and user included attributes
    exclude_attrs: list,
            list of attributes to be excluded in 'table'
    target_attr : string,
            target attribute name containing labels
    k : integer,
        number of folds to be used for crossvalidation

    """
    x,y = get_xy_data(x, y, table, exclude_attrs, target_attr)
    if mg._impute_flag == True:
        # do imputation
        imp = Imputer(missing_values='NaN', strategy='median', axis=0)
        imp.fit(x)
        # replace nan in imputer to 0
        imp.statistics_[np.isnan(imp.statistics_)] = 0.0
        x = imp.transform(x)

    dict_list = []
    max_score = 0
    sel_matcher = matchers[0]
    # header
    header = ['Name', 'Matcher', 'Num folds']
    fold_header = ['Fold ' + str(i+1) for i in range(k)]
    header.extend(fold_header)
    header.append('Mean score')
    #print header

    for m in matchers:
        matcher, scores = cross_validation(m, x, y, metric, k)
        val_list = [matcher.get_name(), matcher, k]
        val_list.extend(scores)
        val_list.append(np.mean(scores))
        #print val_list
        d = OrderedDict(zip(header, val_list))
        #print d
        dict_list.append(d)
        if np.mean(scores) > max_score:
            sel_matcher = m
            max_score = np.mean(scores)
    stats = pd.DataFrame(dict_list)
    stats = stats[header]
    return sel_matcher, stats

def cross_validation(matcher, x, y, metric, k):
    cv = KFold(len(y), k, shuffle=True, random_state=0)
    scores = cross_val_score(matcher.clf, x, y, scoring=metric, cv=cv)
    return matcher, scores



def get_xy_data(x, y, table, exclude_attrs, target_attr):
    if x is not None and y is not None:
        return get_xy_data_prj(x, y)
    elif table is not None and exclude_attrs is not None and target_attr is not None:
        return get_xy_data_ex(table, exclude_attrs, target_attr)
    else:
        raise SyntaxError('The arguments supplied does not match the signatures supported !!!')


def get_xy_data_prj(x, y):
    if x.columns[0] is '_id':
        x = x.values
        x = np.delete(x, 0, 1)
    else:
        x = x.values
    if y is not None:
        if not isinstance(y, pd.Series) and y.columns[0] is '_id':
            y = y.values
            y = np.delete(y, 0, 1)
        else:
            y = y.values
    return x, y

def get_xy_data_ex(table, exclude_attrs, target_attr):
    if not isinstance(exclude_attrs, list):
        exclude_attrs = [exclude_attrs]
    attrs_to_project = mg.diff(table.columns, exclude_attrs)
    table = table.to_dataframe()
    x = table[attrs_to_project].values
    y = table[target_attr].values
    y = y.ravel() # to mute warnings from svm and cross validation
    return x, y
