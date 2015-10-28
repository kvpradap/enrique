import pandas as pd
import numpy as np

def get_attr_types(table):
    """
    Obtain the attribute types of a MTable

    Parameters
    ----------
    table : MTable,
        For which attribute types to be returned

    Returns
    -------
    type_list : dict,
        where key is attribute name and value is type of attribute.
        Type takes one of the following values
        * boolean
        * numeric
        * str_eq_1w : string with average token length 1
        * str_bt_1w_5w : string with average token length > 1 and <= 5
        * str_bt_5w_10w : string with average token length > 5 and <= 10
        * str_gt_10w : string with average token length > 10
        The dictionary also contains a special key "_m_table" and the value
        points to the input table.
    """
    type_list = [get_type(table[col]) for col in table.columns]
    d = dict(zip(table.columns, type_list))
    d['_table'] = table
    return d

def get_attr_corres(table_a, table_b):
    """
    Get attribute correspondences between attributes A and B

    Parameters
    ----------
    table_a, table_b : MTable
        Input MTables for which attribute correspondences should be computed.

    Returns
    -------
    attr_corres : dict,
        It contains 3 keys
        * corres : value points to a list of tuples (containing correspondences); right now the list contains
         only pairs of attributes with exact same names in table_a and table_b
        * ltable : value points to table_a
        * rtable : value points to table_b
    """
    ret_list = []
    for c in table_a.columns:
        if c in table_b.columns:
            ret_list.append((c,c))
    d = dict()
    d['corres'] = ret_list
    d['ltable'] = table_a
    d['rtable'] = table_b
    return d

# Given a pandas series (i.e column in MTable) obtain its type
def get_type(col):
    if not isinstance(col, pd.Series):
        raise ValueError('Input is not of type pandas series')
    # drop NAs
    col = col.dropna()
    # get type for each element and convert it into a set
    type_list = list(set(col.map(type).tolist()))
    if len(type_list) is not 1:
        raise TypeError('Column qualifies to be more than one type')
    else:
        t = type_list[0]
        if t == bool:
            return 'boolean'
        # consider string and unicode as same
        elif t == str or t == unicode:
            # get average token length
            avg_tok_len = pd.Series.mean(col.str.split(' ').apply(len_handle_nan))
            if avg_tok_len == 1:
                return "str_eq_1w"
            elif avg_tok_len <= 5:
                return "str_bt_1w_5w"
            elif avg_tok_len <= 10:
                return "str_bt_5w_10w"
            else:
                return "str_gt_10w"
        else:
            return "numeric"

# Get the length of list, handling NaN
def len_handle_nan(v):
    if isinstance(v, list):
        return len(v)
    else:
        return np.NaN