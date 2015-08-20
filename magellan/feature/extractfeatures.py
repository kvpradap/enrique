import logging
import pandas as pd
import time

import magellan as mg
from magellan.core.mtable import MTable
from magellan.utils.helperfunctions import isJVMStarted

logging.basicConfig(level=logging.INFO)

def extract_feat_vecs(s, attrs_before=None, feat_table=None, attrs_after=None):
    """
    Extract feature vectors

    Parameters
    ----------
    s : MTable,
        labeled virtual MTable or combined blocker output
    attrs_before : list, defaults to None
        List of attribute names from "s" to be included in output table before the feature vector
    feat_table : pandas DataFrame, defaults to None
        List of features to be applied (also see: mg.get_features_for_blocking)
    attrs_after : list, defaults to None
        List of attribute names from "s" to be included in output table after the feature vector

    Returns
    -------
    feature_table : MTable,
        Containing features values (obtained by applying feature fns in feat_table) and attributes as
        mentioned in the input
    """
    # basic checks
    assert isJVMStarted(), 'JVM should be started using init_jvm to compute features'
    ltable = s.get_property('ltable')
    rtable = s.get_property('rtable')
    assert ltable is not None, 'Left table is not set'
    assert rtable is not None, 'Right table is not set'

    if feat_table is None:
        feat_table = mg.get_features_for_blocking(ltable, rtable)

    l_key, r_key = s.get_property('foreign_key_ltable'), s.get_property('foreign_key_rtable')
    start = time.time()
    id_list = [(r[l_key], r[r_key]) for i, r in s.iterrows()]
    end = time.time()
    logging.getLogger(__name__).info('Iterating rows (%d) took %f secs' %(len(s), end - start))

    # compute feature values
    l_df = ltable.to_dataframe()
    r_df = rtable.to_dataframe()
    l_df.set_index(ltable.get_key(), inplace=True, drop=False)
    r_df.set_index(rtable.get_key(), inplace=True, drop=False)

    start = time.time()
    feat_vals = [apply_feat_fns(l_df.ix[x[0]], r_df.ix[x[1]], feat_table) for x in id_list]
    end = time.time()
    logging.getLogger(__name__).info('Applying feature functions took : %f secs' % (end - start))
    table = pd.DataFrame(feat_vals, index=s.index.values)
    # get the feature names and re-arrange columns in that order
    feat_names = list(feat_table['feature_name'])
    table = table[feat_names]
    # insert attrs_before
    if attrs_before:
        if not isinstance(attrs_before, list):
            attrs_before = [attrs_before]
        attrs_before.reverse()
        for a in attrs_before:
            table.insert(0, a, s[a])
    table.insert(0, r_key, s[r_key])
    table.insert(0, l_key, s[l_key])

    # insert attrs after
    if attrs_after:
        if not isinstance(attrs_after, list):
            attrs_after = [attrs_after]
        attrs_after.reverse()
        for a in attrs_after:
            table.insert(len(table.columns), a, s[a])
    # reset the table index
    table.reset_index(inplace=True, drop=True)

    feature_table = MTable(table)
    if s.get_key() not in feature_table.columns:
        feature_table.add_key(s.get_key())
    # metadata
    feature_table._metadata = s._metadata
    feature_table.properties = s.properties
    return feature_table



def apply_feat_fns(t1, t2, feat_dict):
    feat_names = list(feat_dict['feature_name'])
    feat_funcs = list(feat_dict['function'])
    feat_vals = [f(t1,t2) for f in feat_funcs]
    return dict(zip(feat_names, feat_vals))
