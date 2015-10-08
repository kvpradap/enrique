from nose.tools import *
import sys
import os
from tests import mg, path_for_A, path_for_B

def test_readcsv_valid_id():
    A = mg.read_csv(path_for_A, key='ID')
    assert_equal(A.get_key(), 'ID')

@raises(KeyError)
def test_readcsv_key_not_present():
    mg.read_csv(path_for_A, key='ID1')

def test_readcsv_no_id():
    A = mg.read_csv(path_for_A)
    assert_equal(A.get_key(), '_id')

@raises(KeyError)
def test_readcsv_invalid_id():
    mg.read_csv(path_for_A, key='zipcode')

def test_readcsv_fromfile_with_props_mtable():
    A1 = mg.read_csv(path_for_A, key='ID')
    filename = '__tbl__.csv'
    A1.to_csv(filename)
    A2 = mg.read_csv(filename)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(A2.get_key(), 'ID')
    assert_equal(len(A1), len(A2))

def test_readcsv_fromfile_with_props_vtable():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode')
    C1.to_csv(filename, suppress_properties=False)
    C2 = mg.read_csv(filename, ltable=A, rtable=B)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(C2.get_key(), C1.get_key())
    assert_equal(C2.get_property('foreign_key_ltable'), C1.get_property('foreign_key_ltable'))
    assert_equal(C2.get_property('foreign_key_rtable'), C1.get_property('foreign_key_rtable'))

def test_readcsv_fromfile_with_upd_props_mtable():
    filename = '__tbl__.csv'
    A1 = mg.read_csv(path_for_A)
    A1.to_csv(filename)
    A1.set_key('ID')
    A2 = mg.read_csv(filename, key='ID')
    assert_equal(A2.get_key(), 'ID')
    assert_equal(len(A1), len(A2))

def test_readcsv_fromfile_with_upd_props_vtable():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode')
    C1.add_key('_id0')
    C1.to_csv(filename, suppress_properties=False)
    C1.set_key('_id')
    C2 = mg.read_csv(filename, key='_id', ltable=A, rtable=B)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(C2.get_key(), '_id')
    assert_equal(C2.get_property('foreign_key_ltable'), C1.get_property('foreign_key_ltable'))
    assert_equal(C2.get_property('foreign_key_rtable'), C1.get_property('foreign_key_rtable'))

