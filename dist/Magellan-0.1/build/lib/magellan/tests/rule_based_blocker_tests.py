from nose.tools import *

from magellan.tests import mg


def test_rb_block_tables():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    rb = mg.RuleBasedBlocker()
    feature_table = mg.get_features_for_blocking(A, B)
    rb.add_rule(['name_name_mel(ltuple, rtuple) < 0.4',
                 'birth_year_birth_year_lev(ltuple, rtuple) < 0.5'],
                feature_table)
    rb.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) != 1'],
                feature_table)
    C = rb.block_tables(A, B, 'zipcode', 'zipcode')
    s1 = sorted(['_id', 'ltable.ID', 'rtable.ID', 'ltable.zipcode', 'rtable.zipcode'])
    assert_equal(s1, sorted(C.columns))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

    A['dummy'] = 1
    B['dummy'] = 1
    ab = mg.AttrEquivalenceBlocker()
    D = ab.block_tables(A, B, 'dummy','dummy')
    fv = mg.extract_feat_vecs(D,  feat_table=feature_table)
    expected_ids = fv.ix[((fv.name_name_mel >= 0.4) | (fv.birth_year_birth_year_lev >= 0.5)) &
      fv.zipcode_zipcode_exm == 1 ,
      ['ltable.ID', 'rtable.ID',
       ]]
    actual_ids = C[['ltable.ID', 'rtable.ID']]
    ids_exp = list(expected_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    ids_act = list(actual_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    assert_equal(cmp(ids_exp, ids_act), 0)

def test_rb_block_candset():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    E = ab.block_tables(A, B, 'zipcode', 'zipcode')
    rb = mg.RuleBasedBlocker()
    feature_table = mg.get_features_for_blocking(A, B)
    rb.add_rule(['name_name_mel(ltuple, rtuple) < 0.4',
                 'birth_year_birth_year_lev(ltuple, rtuple) < 0.5'],
                feature_table)
    rb.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) != 1'],
                feature_table)
    C = rb.block_candset(E)
    s1 = sorted(['_id', 'ltable.ID', 'rtable.ID'])
    assert_equal(s1, sorted(C.columns))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

    fv = mg.extract_feat_vecs(E,  feat_table=feature_table)
    expected_ids = fv.ix[((fv.name_name_mel >= 0.4) | (fv.birth_year_birth_year_lev >= 0.5)) &
      fv.zipcode_zipcode_exm == 1 ,
      ['ltable.ID', 'rtable.ID',
       ]]
    actual_ids = C[['ltable.ID', 'rtable.ID']]
    ids_exp = list(expected_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    ids_act = list(actual_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    assert_equal(cmp(ids_exp, ids_act), 0)

def test_rb_block_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    rb = mg.RuleBasedBlocker()
    feature_table = mg.get_features_for_blocking(A, B)
    rb.add_rule(['name_name_mel(ltuple, rtuple) < 0.4',
                 'birth_year_birth_year_lev(ltuple, rtuple) < 0.5'],
                feature_table)
    rb.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) != 1'],
                feature_table)

    assert_equal(rb.block_tuples(A.ix[0], B.ix[0]), False)
    assert_equal(rb.block_tuples(A.ix[1], B.ix[1]), True)

def test_rb_block_tables_wi_no_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    rb = mg.RuleBasedBlocker()
    feature_table = mg.get_features_for_blocking(A, B)
    rb.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) >= 0'],
                feature_table)
    C = rb.block_tables(A, B)
    assert_equal(len(C),  0)
    assert_equal(sorted(C.columns), sorted(['_id', 'ltable.ID', 'rtable.ID']))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

def test_rb_block_candset_wi_no_tuples():
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    ab = mg.AttrEquivalenceBlocker()
    C = ab.block_tables(A, B, 'birth_year', 'birth_year')
    rb = mg.RuleBasedBlocker()
    feature_table = mg.get_features_for_blocking(A, B)
    rb.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) >= 0'],
                feature_table)
    D = rb.block_candset(C)
    assert_equal(len(D),  0)
    assert_equal(sorted(D.columns), sorted(['_id', 'ltable.ID', 'rtable.ID']))
    assert_equal(D.get_key(), '_id')
    assert_equal(D.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(D.get_property('foreign_key_rtable'), 'rtable.ID')

