from nose.tools import *
import sys
import os
sys.path.append('/scratch/pradap/python-work/enrique')
import magellan as mg
path_for_A = '../magellan/datasets/table_A.csv'
path_for_B = '../magellan/datasets/table_B.csv'

def test_tocsv_mtable_wi_props():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    A.to_csv(filename)
    A1 = mg.read_csv(filename)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(A1.get_key(), A.get_key())
    assert_equal(len(A1), len(A))

def test_tocsv_vtable_wi_props():
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

def test_tocsv_mtable_wo_props_1():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    A.to_csv(filename, suppress_properties=True)
    A1 = mg.read_csv(filename)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(A1.get_key(), "_id")
    assert_equal(len(A1), len(A))

def test_tocsv_mtable_wo_props_2():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    A.to_csv(filename, suppress_properties=True)
    A1 = mg.read_csv(filename, key='ID')
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(A1.get_key(), "ID")
    assert_equal(len(A1), len(A))


def test_tocsv_vtable_wo_props_1():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode')
    C1.to_csv(filename, suppress_properties=True)
    C2 = mg.read_csv(filename, ltable=A, rtable=B, foreign_key_ltable='ltable.ID',
                     foreign_key_rtable='rtable.ID')
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(C2.get_key(), '_id0')
    assert_equal(C2.get_property('foreign_key_ltable'), C1.get_property('foreign_key_ltable'))
    assert_equal(C2.get_property('foreign_key_rtable'), C1.get_property('foreign_key_rtable'))


def test_tocsv_vtable_wo_props_2():
    filename = '__tbl__.csv'
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode')
    C1.to_csv(filename, suppress_properties=True)
    C2 = mg.read_csv(filename, ltable=A, rtable=B, foreign_key_ltable='ltable.ID',
                     foreign_key_rtable='rtable.ID', key='_id')
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(C2.get_key(), '_id')
    assert_equal(C2.get_property('foreign_key_ltable'), C1.get_property('foreign_key_ltable'))
    assert_equal(C2.get_property('foreign_key_rtable'), C1.get_property('foreign_key_rtable'))
