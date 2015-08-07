import magellan as mg
import numpy as np
import pandas as pd

from sklearn.cross_validation import KFold, cross_val_score

def select_matcher(matchers, x=None, y=None, table=None, exclude_attrs=None, target_attr=None, k=5):
    x,y = get_xy_data(x, y, table, exclude_attrs, target_attr)


    pass


def cross_validation(matcher, x, y, k):
    cv = KFold(len(y), k, shuffle=True, random_state=0)
    scores = cross_val_score(matcher.clf, x, y, cv=cv)
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
    return x, y
