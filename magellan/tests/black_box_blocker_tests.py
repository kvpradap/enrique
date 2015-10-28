from nose.tools import *

from magellan.tests import mg
from magellan.feature.simfunctions import  monge_elkan


def block_fn(x, y):
    if (monge_elkan(x['name'], y['name']) < 0.4):
        return True
    else:
        return False
def evil_block_fn(x, y):
    return True

def test_bb_block_tables():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(block_fn)
    C = bb.block_tables(A, B, 'zipcode', 'zipcode')
    s1 = sorted(['_id', 'ltable.ID', 'rtable.ID', 'ltable.zipcode', 'rtable.zipcode'])
    assert_equal(s1, sorted(C.columns))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

    feature_table = mg.get_features_for_blocking(A, B)
    A['dummy'] = 1
    B['dummy'] = 1
    ab = mg.AttrEquivalenceBlocker()
    D = ab.block_tables(A, B, 'dummy','dummy')
    fv = mg.extract_feat_vecs(D,  feature_table=feature_table)
    expected_ids = fv.ix[(fv.name_name_mel >= 0.4) ,
      ['ltable.ID', 'rtable.ID']]
    actual_ids = C[['ltable.ID', 'rtable.ID']]
    ids_exp = list(expected_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    ids_act = list(actual_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    assert_equal(cmp(ids_exp, ids_act), 0)

def test_bb_block_candset():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    E = ab.block_tables(A, B, 'zipcode', 'zipcode')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(block_fn)
    C = bb.block_candset(E)
    feature_table = mg.get_features_for_blocking(A, B)
    fv = mg.extract_feat_vecs(C, feature_table=feature_table)
    expected_ids = fv.ix[(fv.name_name_mel >= 0.4) ,
      ['ltable.ID', 'rtable.ID']]
    actual_ids = C[['ltable.ID', 'rtable.ID']]
    ids_exp = list(expected_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    ids_act = list(actual_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    assert_equal(cmp(ids_exp, ids_act), 0)

def test_bb_block_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(block_fn)
    assert_equal(bb.block_tuples(A.ix[0], B.ix[0]), True)
    assert_equal(bb.block_tuples(A.ix[2], B.ix[1]), False)


def test_bb_block_tables_wi_no_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(evil_block_fn)
    C = bb.block_tables(A, B)
    assert_equal(len(C),  0)
    assert_equal(sorted(C.columns), sorted(['_id', 'ltable.ID', 'rtable.ID']))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

def test_bb_block_candset_wi_no_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    C = ab.block_tables(A, B, 'birth_year', 'birth_year')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(evil_block_fn)
    D = bb.block_candset(C)
    assert_equal(len(D),  0)
    assert_equal(sorted(D.columns), sorted(['_id', 'ltable.ID', 'rtable.ID']))
    assert_equal(D.get_key(), '_id')
    assert_equal(D.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(D.get_property('foreign_key_rtable'), 'rtable.ID')

