from nose.tools import *
from tests import mg
import numpy as np

def test_ab_block_tables():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    C = ab.block_tables(A, B, 'zipcode', 'zipcode', 'zipcode', 'zipcode')
    s1 = sorted(['_id', 'ltable.ID', 'rtable.ID', 'ltable.zipcode', 'rtable.zipcode'])
    assert_equal(s1, sorted(C.columns))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')
    k1 = np.array(C[['ltable.zipcode']])
    k2 = np.array(C[['rtable.zipcode']])
    assert_equal(all(k1 == k2), True)

def test_ab_block_candset():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    C = ab.block_tables(A, B, 'zipcode', 'zipcode', ['zipcode', 'birth_year'], ['zipcode', 'birth_year'])
    D = ab.block_candset(C, 'birth_year', 'birth_year')
    s1 = sorted(['_id', 'ltable.ID', 'rtable.ID', 'ltable.zipcode', 'ltable.birth_year', 'rtable.zipcode',
                 'rtable.birth_year'])
    assert_equal(s1, sorted(D.columns))
    assert_equal(D.get_key(), '_id')
    assert_equal(D.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(D.get_property('foreign_key_rtable'), 'rtable.ID')
    k1 = np.array(D[['ltable.birth_year']])
    k2 = np.array(D[['rtable.birth_year']])
    assert_equal(all(k1 == k2), True)

def test_ab_block_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    assert_equal(ab.block_tuples(A.ix[1], B.ix[2], 'zipcode', 'zipcode'), False)
    assert_equal(ab.block_tuples(A.ix[2], B.ix[2], 'zipcode', 'zipcode'), True)


def test_ab_block_tables_wi_no_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    C = ab.block_tables(A, B, 'name', 'name')
    assert_equal(len(C),  0)
    assert_equal(sorted(C.columns), sorted(['_id', 'ltable.ID', 'rtable.ID']))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')


def test_ab_block_candset_wi_no_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    C = ab.block_tables(A, B, 'name', 'name')
    D = ab.block_candset(C, 'birth_year', 'birth_year')
    assert_equal(len(D),  0)
    assert_equal(sorted(D.columns), sorted(['_id', 'ltable.ID', 'rtable.ID']))
    assert_equal(D.get_key(), '_id')
    assert_equal(D.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(D.get_property('foreign_key_rtable'), 'rtable.ID')
