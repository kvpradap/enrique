import pandas as pd

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
    pass

def lr_tables(blocker_output_list):
    id_l = [id(c.get_property('ltable')) for c in blocker_output_list]
    id_l = set(id_l)
    assert len(id_l) is 1, 'Candidate set list contains different left tables'
    id_r = [id(c.get_property('rtable')) for c in blocker_output_list]
    id_r = set(id_r)
    assert len(id_r) is 1, 'Candidate set list contains different right tables'
    #return blocker_output_list[0].left_table, blocker_output_list[1].right_table
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

def get_dict(left, right, col_l, col_r):
    dl = left[col_l].to_dict()
    dr = right[col_r].to_dict()
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
    l = sorted(set(col_l).difference([id_l]))
    l = ['ltable.'+ x for x in l]
    fin.extend(l)
    r = sorted(set(col_r).difference([id_r]))
    r = ['rtable.'+ x for x in r]
    fin.extend(r)
    return fin