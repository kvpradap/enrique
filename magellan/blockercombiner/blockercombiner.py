import pandas as pd

import magellan as mg
from magellan.core.mtable import MTable

def combine_block_outputs_via_union(blocker_output_list):
    """
    Combine blocker outputs by unioning ltable, rtable ids in candidate set

    Parameters
    ----------
    blocker_output_list : list
        List of blocker outputs

    Returns
    -------
    combined_blocker_output : MTable
        With combined blocker outputs

    Notes
    -----
    Combined_blocker_output contains the following attributes
    * _id
    * combined id pairs (ltable.id, rtabled.id) from list of blocker outputs
    * union of non-id attributes from each of blocker output
    """
    ltable, rtable = lr_tables(blocker_output_list)
    # get the attribute names in blocker output that represents ltable, rtable
    l_key = 'ltable.' + ltable.get_key()
    r_key = 'rtable.' + rtable.get_key()

    # get the set of id pairs from all blocker output list
    id_set = set([(r[l_key], r[r_key]) for c in blocker_output_list for i, r in c.iterrows()])

    # get the union of attribute names from blocker output list
    col_set = set([x for c in blocker_output_list for x in c.columns])
    l_col, r_col = lr_cols(col_set)

    # convert ltable, rtable to dfs and set index
    l_df = ltable.to_dataframe()
    l_df.set_index(ltable.get_key(), inplace=True, drop=False)
    r_df = rtable.to_dataframe()
    r_df.set_index(rtable.get_key(), inplace=True, drop=False)

    # get the l_col, r_col from ltable and rtable respectively
    dict_list = [get_dict(l_df.ix[x[0]], r_df.ix[x[1]], l_col, r_col) for x in id_set]

    # convert list of dicts to dataframe
    table = pd.DataFrame(dict_list)

    # get the final column names for output table
    f_cols = fin_cols(l_col, r_col, ltable.get_key(), rtable.get_key())

    # project df and convert to MTable
    table = MTable(table[f_cols])
    #key_name = table._get_name_for_key(table.columns)
    #table.add_key(key_name)

    # set metadata
    table.set_property('ltable', ltable)
    table.set_property('rtable', rtable)
    table.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
    table.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())

    return table

def lr_tables(blocker_output_list):
    # get ids of all ltables from blocker output list
    id_l = [id(c.get_property('ltable')) for c in blocker_output_list]
    # convert to set
    id_l = set(id_l)
    # check its length is 1 == all the ltables are same
    assert len(id_l) is 1, 'Candidate set list contains different left tables'
    # do the same for rtable
    id_r = [id(c.get_property('rtable')) for c in blocker_output_list]
    id_r = set(id_r)
    assert len(id_r) is 1, 'Candidate set list contains different right tables'

    # since all the ltables and rtables are same, return the ltable and rtable from first blocker output
    return blocker_output_list[0].get_property('ltable'), blocker_output_list[0].get_property('rtable')

def lr_cols(col_set):
    cols = sorted(col_set)
    col_l = [get_col(s, 'ltable.') for s in cols]
    col_l = [x for x in col_l if x is not None]

    col_r = [get_col(s, 'rtable.') for s in cols]
    col_r = [x for x in col_r if x is not None]

    return col_l, col_r

def get_col(s, p):
    if s.startswith(p):
        return s[len(p):]
    return None

def get_dict(ltable, rtable, l_col, r_col):
    dl = ltable[l_col].to_dict()
    dr = rtable[r_col].to_dict()
    cl = ['ltable.' + k for k in dl.keys()]
    cr = ['rtable.' + k for k in dr.keys()]
    vl = [v for v in dl.values()]
    vr = [v for v in dr.values()]
    c = cl
    c.extend(cr)
    v = vl
    v.extend(vr)
    d = dict(zip(c,v))
    return d

def fin_cols(col_l, col_r, id_l, id_r):
    fin = ['ltable.'+id_l, 'rtable.'+id_r]
    l = mg.diff(col_l, [id_l])
    l = ['ltable.'+ x for x in l]
    fin.extend(l)

    r = mg.diff(col_r, [id_r])
    r = ['rtable.'+ x for x in r]
    fin.extend(r)
    return fin