from nose.tools import *
from tests import mg, path_for_A, path_for_B

def test_bl_combiner_wo_added_fields():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode', ['name'], ['name'])
    C2 = ab.block_tables(A, B, 'hourly_wage', 'hourly_wage', ['zipcode'], ['zipcode'])
    C3 = ab.block_tables(A, B, 'birth_year', 'birth_year', ['hourly_wage'], ['hourly_wage'])
    C = mg.combine_block_outputs_via_union([C1, C2, C3])
    s = ['_id', 'ltable.ID', 'rtable.ID', 'ltable.name', 'ltable.zipcode', 'ltable.hourly_wage',
         'rtable.name', 'rtable.zipcode', 'rtable.hourly_wage']
    assert_equal(sorted(s) == sorted(C.columns), True)
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

def test_bl_combiner_wi_added_fields():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode', ['name'], ['name'])
    C1['dummy1'] = 0
    C2 = ab.block_tables(A, B, 'hourly_wage', 'hourly_wage', ['zipcode'], ['zipcode'])
    C2['dummy2'] = 1
    C3 = ab.block_tables(A, B, 'birth_year', 'birth_year', ['hourly_wage'], ['hourly_wage'])
    C3['dummy3'] = 2
    C = mg.combine_block_outputs_via_union([C1, C2, C3])
    s = ['_id', 'ltable.ID', 'rtable.ID', 'ltable.name', 'ltable.zipcode', 'ltable.hourly_wage',
         'rtable.name', 'rtable.zipcode', 'rtable.hourly_wage']
    assert_equal(sorted(s) == sorted(C.columns), True)
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

def test_bl_combiner_wi_no_fields():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'zipcode', 'zipcode')
    C2 = ab.block_tables(A, B, 'hourly_wage', 'hourly_wage')
    C3 = ab.block_tables(A, B, 'birth_year', 'birth_year')
    C = mg.combine_block_outputs_via_union([C1, C2, C3])
    s = ['_id', 'ltable.ID', 'rtable.ID']
    assert_equal(sorted(s) == sorted(C.columns), True)
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

def test_bl_combiner_wi_no_tuples():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'name', 'name')
    C = mg.combine_block_outputs_via_union([C1, C1, C1])
    s = ['_id', 'ltable.ID', 'rtable.ID']
    assert_equal(sorted(s) == sorted(C.columns), True)
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

def test_bl_combiner_wi_no_tuples_in_one_of_blockers():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    C1 = ab.block_tables(A, B, 'name', 'name')
    C2 = ab.block_tables(A, B, 'hourly_wage', 'hourly_wage')
    C3 = ab.block_tables(A, B, 'birth_year', 'birth_year')
    C = mg.combine_block_outputs_via_union([C1, C2, C3])
    s = ['_id', 'ltable.ID', 'rtable.ID']
    assert_equal(sorted(s) == sorted(C.columns), True)
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')
