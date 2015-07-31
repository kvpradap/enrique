import pandas as pd

from magellan.core.mtable import MTable

def block_union_combiner(vtable_list):
    # check and get ltable and rtable
    ltable, rtable = lr_tables(vtable_list)
    l_key = 'ltable.' + ltable.get_key()
    r_key = 'rtable.' + rtable.get_key()
    # get the set of id pairs
    id_set = set([(r[l_key], r[r_key]) for c in vtable_list for i, r in c.iterrows()])
    # get the union of columns
    col_set = set([x for c in vtable_list for x in c.columns])
    l_col, r_col = lr_cols(col_set)
    dict_list = [get_dict(ltable.ix[x[0]], rtable.ix[x[1]], l_col, r_col) for x in id_set]
    table = pd.DataFrame(dict_list)
    f_cols = fin_cols(l_col, r_col, ltable.get_key(), rtable.get_key())

    table = MTable(table[f_cols]) # need to check
    table.add_key('_m_id')

    table.set_property('ltable', ltable)
    table.set_property('rtable', rtable)
    table.set_property('foreign_keys', [l_key, r_key])

    return table

# --------------------------------------------------------------------------------
# helper functions


def lr_tables(vtable_list):
    l_id = set([id(c.get_property('ltable')) for c in vtable_list])
    r_id = set([id(c.get_property('rtable')) for c in vtable_list])
    assert len(l_id) is 1, 'Candidate set contains different ltables'
    assert len(r_id) is 1, 'Candidate set contains different rtables'
    return vtable_list[0].get_property('ltable'), vtable_list[0].get_property('rtable')

def lr_cols(col_set):
    cols = sorted(col_set)
    l_col = [get_col(s, 'ltable.') for s in cols]
    l_col = [x for x in l_col if x is not None]

    r_col = [get_col(s, 'rtable.') for s in cols]
    r_col = [x for x in r_col if x is not None]

    return l_col, r_col

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

def fin_cols(l_col, r_col, l_id, r_id):
    fin = ['ltable.'+l_id, 'rtable.'+r_id]
    l = sorted(set(l_col).difference([l_id]))
    l = ['ltable.'+ x for x in l]
    fin.extend(l)
    r = sorted(set(r_col).difference([r_id]))
    r = ['rtable.'+ x for x in r]
    fin.extend(r)
    return fin