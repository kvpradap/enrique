# imports
import pandas as pd
import numpy as np


from magellan.blocker.blocker import Blocker
from magellan.core.mtable import MTable

class AttrEquivBlocker(Blocker):
    def block_tables(self, ltable, rtable, l_block_attr, r_block_attr,
                     l_output_attrs=None, r_output_attrs=None):

        assert ltable is not None, 'ltable is None'
        assert rtable is not None, 'rtable is None'

        # check whether keys are set
        assert ltable.get_key() is not None, 'Key is not set for left table'
        assert rtable.get_key() is not None, 'Key is not set for right table'

        if l_block_attr is not list:
            l_block_attr = [l_block_attr]
        if r_block_attr is not list:
            r_block_attr = [r_block_attr]
        if l_output_attrs is None:
            l_output_attrs = []
        if r_output_attrs is None:
            r_output_attrs = []

        # check the integrity of attrs
        check_attrs(ltable.get_attr_names(), rtable.get_attr_names(), l_block_attr, r_block_attr,
                    l_output_attrs, r_output_attrs)

        # remove nans
        m_ltable = rem_nan(ltable, l_block_attr)
        m_rtable = rem_nan(rtable, r_block_attr)

        # block
        candset = pd.merge(m_ltable, m_rtable, left_on=l_block_attr, right_on=r_block_attr,
                           suffixes=('_ltable', '_rtable'))

        # get the columns to be projected and the name of those columns
        ret_cols = ret_attrs(candset.columns, l_output_attrs, r_output_attrs,
                             ltable.get_key(), rtable.get_key())
        fin_cols = fin_attrs(candset.columns, l_output_attrs, r_output_attrs,
                             ltable.get_key(), rtable.get_key())

        vtable = MTable(candset[ret_cols])# need to check this behavior
        vtable.properties=dict()
        vtable.add_key('_m_id')
        vtable.columns = fin_cols

        vtable.set_property('ltable', ltable)
        vtable.set_property('rtable', rtable)
        vtable.set_property('foreign_keys', [ltable.get_key(), rtable.get_key()])

        return vtable

    def block_candset(self, vtable, l_block_attr, r_block_attr):
        ltable = vtable.get_property('ltable')
        rtable = vtable.get_property('rtable')

        assert ltable is not None, 'ltable is None'
        assert rtable is not None, 'rtable is None'

        # check whether keys are set
        assert ltable.get_key() is not None, 'Key is not set for left table'
        assert rtable.get_key() is not None, 'Key is not set for right table'

        if l_block_attr is not list:
            l_block_attr = [l_block_attr]
        if r_block_attr is not list:
            r_block_attr = [r_block_attr]

        check_attrs(ltable.get_attr_names(), rtable.get_attr_names(), l_block_attr, r_block_attr,
                    [], [])

        # construct key strings that can be queried in the candidate set table
        l_key = 'ltable.' + ltable.get_key()
        r_key = 'rtable.' + rtable.get_key()
        valid = []
        for idx, row in vtable.iterrows():
            l_val = row[l_key] # assumes that index is set over key !!!
            r_val = row[r_key]
            # tuple below is for the case when block_attr is list : CAN BE REMOVED
            l_tup = tuple(ltable.ix[l_val, l_block_attr])
            r_tup = tuple(rtable.ix[r_val, r_block_attr])
            if np.NaN in l_tup or np.NaN in r_tup:
                valid.append(False)
            elif l_tup == r_tup:
                valid.append(True)
            else:
                valid.append(False)
        table = vtable[valid]

        table = table.drop('_m_id', 1)
        table.reset_index(drop=True, inplace=True)
        table.add_key('_m_id')


        return table

    def block_tuples(self, ltuple, rtuple, l_block_attr, r_block_attr):
        return ltuple[l_block_attr] != rtuple[r_block_attr]


# check integrity of attr names given as parameters
def check_attrs(l_attrs, r_attrs, l_block_attr, r_block_attr,
                l_output_attrs, r_output_attrs):

    assert l_block_attr is not None, 'Left block attribute cannot be None'
    assert r_block_attr is not None, 'Right block attribute cannot be None'

    assert set(l_block_attr).issubset(l_attrs) is True, 'Left block attribute is not in left table attrs'
    assert set(l_block_attr).issubset(r_attrs) is True, 'Right block attribute is not in right table attrs'

    if l_output_attrs is not None:
        assert set(l_output_attrs).issubset(l_attrs) is True, 'Left output attrs do not form a subset of left ' \
                                                              'table attrs'
    if r_output_attrs is not None:
        assert set(r_output_attrs).issubset(r_attrs) is True, 'Right output attrs do not form a subset of Right ' \
                                                              'table attrs'
    return True

# remove rows with nans at block attr
def rem_nan(table, attr):
    indices = [list(table.index.values[np.where(table[x].notnull())[0]]) for x in attr]
    # the following statement is only for the case where there are multiple block attrs - CAN BE REMOVED
    indices = sorted(set.intersection(*map(set, indices)))
    return table.ix[indices]

# get attrs to be retained in candidate set
def ret_attrs(cand_cols, l_output_attrs, r_output_attrs, l_key, r_key,):
    l_key = [l_key]
    r_key = [r_key]
    retain = []
    # list difference function
    diff = lambda l1,l2: [x for x in l1 if x not in l2]

    l_output_attrs = diff(l_output_attrs, l_key)
    r_output_attrs = diff(r_output_attrs, r_key)


    l_id = [retain_names(x, cand_cols, '_ltable') for x in l_key]
    r_id = [retain_names(x, cand_cols, '_rtable') for x in r_key]

    l_attrs = [retain_names(x, cand_cols, '_ltable') for x in l_output_attrs]
    r_attrs = [retain_names(x, cand_cols, '_rtable') for x in r_output_attrs]

    retain.extend(l_id)
    retain.extend(r_id)
    retain.extend(l_attrs)
    retain.extend(r_attrs)

    return retain

def fin_attrs(cand_cols, l_output_attrs, r_output_attrs, l_key, r_key,):
    l_key = [l_key]
    r_key = [r_key]
    fin = ['_m_id']
    # list difference function
    diff = lambda l1,l2: [x for x in l1 if x not in l2]

    l_output_attrs = diff(l_output_attrs, l_key)
    r_output_attrs = diff(r_output_attrs, r_key)

    l_id = [final_names(x, 'ltable.') for x in l_key]
    r_id = [final_names(x, 'rtable.') for x in r_key]

    l_attrs = [final_names(x, 'ltable.') for x in l_output_attrs]
    r_attrs = [final_names(x, 'rtable.') for x in r_output_attrs]

    fin.extend(l_id)
    fin.extend(r_id)
    fin.extend(l_attrs)
    fin.extend(r_attrs)

    return fin




def retain_names(inp_name, colnames, suffix):
    if inp_name in colnames:
        return inp_name
    else:
        name_str = str(inp_name)
        name_str += suffix
    return name_str

def final_names(inp_name, prefix):
    name_str = str(inp_name)
    name_str = prefix + name_str
    return name_str