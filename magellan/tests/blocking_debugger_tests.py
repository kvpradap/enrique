from nose.tools import *
from magellan.debugblocker.blocking_debugger import *

import pandas as pd


def test_get_kgram():
    doc = pd.Series(['aaa', 'bbb'])
    features = [0, 1]
    expected_kgram_set = set(['aaa', 'aa ', 'a b', ' bb', 'bbb'])
    assert_equal(get_kgram(doc, features, 3), expected_kgram_set)

    doc = pd.Series(['aa'])
    features = [0]
    expected_kgram_set = set()
    assert_equal(get_kgram(doc, features, 3), expected_kgram_set)

    doc = pd.Series(['abc', 'not useful', 'abc', 'skip', 'abc'])
    features = [0, 2, 4]
    expected_kgram_set = set(['abc', 'bc ', 'c a', ' ab'])
    assert_equal(get_kgram(doc, features, 3), expected_kgram_set)

    doc = pd.Series(['abc', 11.88, 1234567890, 'end'])
    features = [0, 1, 2, 3]
    expected_kgram_set = set(
        ['abc', 'bc ', 'c 1', ' 12', '12 ', '2 1', '123', '234', '345', '456', '567', '678', '789', '890', '90 ', '0 e',
         ' en', 'end'])
    assert_equal(get_kgram(doc, features, 3), expected_kgram_set)

    doc = pd.Series([None, None, None, None])
    features = [0, 1, 2, 3]
    expected_kgram_set = set(['   '])
    assert_equal(get_kgram(doc, features, 3), expected_kgram_set)


def test_jaccard_sim():
    lset = set(['abc', 'lll'])
    rset = set(['abc', 'lll'])
    assert_equal(jaccard_kgram_sim(lset, rset), 1.0)

    lset = set()
    rset = set()
    assert_equal(jaccard_kgram_sim(lset, rset), 0.0)

    lset = set(['123'])
    rset = set()
    assert_equal(jaccard_kgram_sim(lset, rset), 0.0)

    lset = set([123, 'abc', 56.7])
    rset = set(['abc', ''])
    assert_equal(jaccard_kgram_sim(lset, rset), 0.25)


# Test output when at least one table is empty.
def test_debug_blocker_case_1():
    A = MTable([])
    B = MTable([])
    C = MTable([])
    assert_raises(StandardError, debug_blocker, A, B, C, 10)

    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    A = MTable(data)
    B = MTable([])
    assert_raises(StandardError, debug_blocker, A, B, C, 10)


# Test output when all fields are numeric types
def test_debug_blocker_case_2():
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    columns = ['_id', 'a', 'b', 'c']
    A = MTable(data)
    B = MTable(data)
    A.columns = columns
    B.columns = columns
    blocker = mg.AttrEquivalenceBlocker()
    C = blocker.block_tables(A, B, 'a', 'a')
    assert_raises(StandardError, debug_blocker, A, B, C, 10)


# Test output when each concatenated doc 3gram set is empty. The output MTable
# should also be empty.
def test_debug_blocker_case_3():
    data = [[1, '2', 3], [4, 5, 6], [7, 8, 9]]
    columns = ['_id', 'a', 'b', 'c']
    A = MTable(data)
    B = MTable(data)
    A.columns = columns
    B.columns = columns
    blocker = mg.AttrEquivalenceBlocker()
    C = blocker.block_tables(A, B, 'a', 'a')
    assert_equal(debug_blocker(A, B, C, 10).empty, True)


# assert_raises(StandardError, debug_blocker, A, B, C, 10)

# Test output when
#	1. two tables have the same schema, and each table has at least one non-empty kgram set.
#	2. one kgram set S in one table shares nothing with all kgram sets in the other table. (In
#	   this condition, the set S should be SKIIPED since all sim score would be 0.0, and we will
#	   not put this 0.0 sim score into the suggestion list).
def test_debug_blocker_case_4():
    data = [[1, 'asdf', 3], [4, 5, 'asdf'], [7, 8, 9]]
    columns = ['_id', 'a', 'b', 'c']
    A = MTable(data)
    B = MTable(data)
    A.columns = columns
    B.columns = columns
    blocker = mg.AttrEquivalenceBlocker()
    C = blocker.block_tables(A, B, 'a', 'a')
    actual = debug_blocker(A, B, C, output_size=10)
    expected_data = [[0, 1.0 / 3, 0, 1, 'asdf', 5, 3, 'asdf'], [1, 1.0 / 3, 1, 0, 5, 'asdf', 'asdf', 3]]
    expected_columns = ['_id', 'similarity', 'ltable._id', 'rtable._id', 'ltable.b', 'rtable.b', 'ltable.c', 'rtable.c']
    assert_equal(list(actual.columns), expected_columns)
    for i in range(len(actual)):
        assert_equal(list(actual.ix[i]), expected_data[i])


# Test output given a normal table. In this test, the user will not provide field_corres_list.
def test_debug_blocker_case_5():
    l1 = [1, 'James', 'Doe', 20, '1210 W. Dayton', '(608)123-4567', 53706]
    l2 = [2, 'John', 'Smith', 35, '2345 Univ. Ave.', '609-111-1111', 53725]
    l3 = [3, 'Kate', 'Swift', 30, '15 Regent Street, APT 10', '6086096100', 53710]
    r1 = [1, 'Swift', 'Katherine', 30, '(608)609-6100', '15 Regent St.', 53710]
    r2 = [2, 'Doe', 'Jimmy', 21, '608-123-4567', 'Dept. of Comp. Sci., 1210 W. Dayton St.', 53706]
    r3 = [3, 'Smith', 'John', 35, '609,111,1111', '2345 University Ave.', 53725]
    r4 = [4, 'Gates', 'William', 60, '(608)610-6100', None, None]
    ltable_data = [l1, l2, l3]
    rtable_data = [r1, r2, r3, r4]
    ltable_columns = ['ID', 'first name', 'last name', 'age', 'address', 'phone', 'zipcode']
    rtable_columns = ['ID', 'last name', 'first name', 'age', 'cellphone', 'address', 'zipcode']
    lframe = pd.DataFrame(ltable_data)
    lframe.columns = ltable_columns
    rframe = pd.DataFrame(rtable_data)
    rframe.columns = rtable_columns
    ltable = MTable(lframe, key='ID')
    rtable = MTable(rframe, key='ID')
    blocker = mg.AttrEquivalenceBlocker()
    cand_set = blocker.block_tables(ltable, rtable, 'zipcode', 'age')
    assert_equal(len(cand_set), 0)
    corres_list = get_field_correspondence_list(ltable, rtable, None)
    assert_equal(corres_list, [('ID', 'ID'), ('first name', 'first name'), ('last name', 'last name'),
                               ('age', 'age'), ('address', 'address'), ('zipcode', 'zipcode')])
    ltable_col_dict = build_col_name_index_dict(ltable)
    rtable_col_dict = build_col_name_index_dict(rtable)
    filter_corres_list(ltable, rtable, ltable_col_dict, rtable_col_dict, corres_list)
    assert_equal(corres_list, [('ID', 'ID'), ('first name', 'first name'), ('last name', 'last name'),
                               ('address', 'address')])
    expected_columns = ['_id', 'similarity', 'ltable.ID', 'rtable.ID',
                        'ltable.first name', 'rtable.first name', 'ltable.last name', 'rtable.last name',
                        'ltable.address', 'rtable.address']
    expected_data = [[0, 21.0 / 32, 2, 3, 'John', 'John', 'Smith', 'Smith', '2345 Univ. Ave.', '2345 University Ave.'],
                     [1, 19.0 / 40, 3, 1, 'Kate', 'Katherine', 'Swift', 'Swift', '15 Regent Street, APT 10',
                      '15 Regent St.'],
                     [2, 16.0 / 53, 1, 2, 'James', 'Jimmy', 'Doe', 'Doe', '1210 W. Dayton',
                      'Dept. of Comp. Sci., 1210 W. Dayton St.']]
    actual = debug_blocker(ltable, rtable, cand_set, output_size=3)
    assert_equal(list(actual.columns), expected_columns)
    for i in range(len(actual)):
        assert_equal(list(actual.ix[i]), expected_data[i])


# Test output given a normal table. In this test, the user provides the field_corres_list.
def test_debug_blocker_case_6():
    l1 = [1, 'James', 'Doe', 20, '1210 W. Dayton', '(608)123-4567', 53706]
    l2 = [2, 'John', 'Smith', 35, '2345 Univ. Ave.', '609-111-1111', 53725]
    l3 = [3, 'Kate', 'Swift', 30, '15 Regent Street, APT 10', '6086096100', 53710]
    r1 = [1, 'Swift', 'Katherine', 30, '(608)609-6100', '15 Regent St.', 53710]
    r2 = [2, 'Doe', 'Jimmy', 21, '608-123-4567', 'Dept. of Comp. Sci., 1210 W. Dayton St.', 53706]
    r3 = [3, 'Smith', 'John', 35, '609,111,1111', '2345 University Ave.', 53725]
    r4 = [4, 'Gates', 'William', 60, '(608)610-6100', None, None]
    ltable_data = [l1, l2, l3]
    rtable_data = [r1, r2, r3, r4]
    ltable_columns = ['ID', 'first name', 'last name', 'age', 'address', 'phone', 'zipcode']
    rtable_columns = ['ID', 'last name', 'first name', 'age', 'cellphone', 'address', 'zipcode']
    lframe = pd.DataFrame(ltable_data)
    lframe.columns = ltable_columns
    rframe = pd.DataFrame(rtable_data)
    rframe.columns = rtable_columns
    ltable = MTable(lframe, key='ID')
    rtable = MTable(rframe, key='ID')
    blocker = mg.AttrEquivalenceBlocker()
    cand_set = blocker.block_tables(ltable, rtable, 'zipcode', 'cellphone')
    assert_equal(len(cand_set), 0)

    user_input_field_list = [('age', 'age')]
    assert_raises(StandardError, get_field_correspondence_list(ltable, rtable, user_input_field_list))

    user_input_field_list = [('ID', 'ID'), ('first name', 'first name'), ('last name', 'last name'),
                             ('age', 'age'), ('phone', 'cellphone'), ('address', 'address'), ('zipcode', 'zipcode')]
    corres_list = get_field_correspondence_list(ltable, rtable, user_input_field_list)
    assert_equal(corres_list, [('ID', 'ID'), ('first name', 'first name'), ('last name', 'last name'),
                               ('age', 'age'), ('phone', 'cellphone'), ('address', 'address'), ('zipcode', 'zipcode')])

    ltable_col_dict = build_col_name_index_dict(ltable)
    rtable_col_dict = build_col_name_index_dict(rtable)
    filter_corres_list(ltable, rtable, ltable_col_dict, rtable_col_dict, corres_list)
    assert_equal(corres_list, [('ID', 'ID'), ('first name', 'first name'), ('last name', 'last name'),
                               ('phone', 'cellphone'), ('address', 'address')])

    expected_columns = ['_id', 'similarity', 'ltable.ID', 'rtable.ID',
                        'ltable.first name', 'rtable.first name', 'ltable.last name', 'rtable.last name',
                        'ltable.phone', 'rtable.cellphone', 'ltable.address', 'rtable.address']
    expected_data = [
        [0, 13.0 / 23, 2, 3, 'John', 'John', 'Smith', 'Smith', '609-111-1111', '609,111,1111', '2345 Univ. Ave.',
         '2345 University Ave.'],
        [1, 10.0 / 31, 1, 2, 'James', 'Jimmy', 'Doe', 'Doe', '(608)123-4567', '608-123-4567', '1210 W. Dayton',
         'Dept. of Comp. Sci., 1210 W. Dayton St.'],
        [2, 11.0 / 35, 3, 1, 'Kate', 'Katherine', 'Swift', 'Swift', '6086096100', '(608)609-6100',
         '15 Regent Street, APT 10', '15 Regent St.']]
    actual = debug_blocker(ltable, rtable, cand_set, output_size=3, attr_corres = user_input_field_list)
    assert_equal(list(actual.columns), expected_columns)
    for i in range(len(actual)):
        assert_equal(list(actual.ix[i]), expected_data[i])


# Test feature selection.
def test_debug_blocker_case_7():
    ltable_columns = ['ln1', 'ls1', 'ls2', 'ln2', 'ln3', 'ln4', 'ls3', 'ln5', 'ls4', 'ls5', 'ls6', 'ln6', 'ls7', 'ln7']
    rtable_columns = ['rn1', 'rn2', 'rn3', 'rn4', 'rn5', 'rn6', 'rn7', 'rs1', 'rs2', 'rs3', 'rs4', 'rs5', 'rs6', 'rs7']
    l1 = [1, 's11', None, 1, 2, 3, None, 1, 's41', 's51', None, 5, 's71', 6]
    l2 = [2, 's12', 's22', 1, 2, 3, 's32', 1, 's42', 's52', None, 5, 's72', 6]
    l3 = [3, 's13', 's23', 1, 2, 3, None, 1, 's42', None, 's63', 5, 's73', 6]
    r1 = [1, 1, 2, 3, 4, 5, 6, None, None, None, 's41', 's51', 's61', 's71']
    r2 = [2, 1, 2, 3, 4, 5, 6, 's12', None, 's32', None, 's52', 's62', None]
    r3 = [3, 1, 2, 3, 4, 5, 6, 's13', 's23', None, 's43', 's52', None, 's73']
    r4 = [4, 1, 2, 3, 4, 5, 6, 's14', 's24', 's32', 's44', 's52', 's64', None]
    lframe = pd.DataFrame([l1, l2, l3])
    rframe = pd.DataFrame([r1, r2, r3, r4])
    lframe.columns = ltable_columns
    rframe.columns = rtable_columns
    ltable = MTable(lframe, key='ln1')
    rtable = MTable(rframe, key='rn1')
    user_input_field_list = []
    expected_filtered_corres_list = [('ln1', 'rn1')]
    for i in range(7):
        user_input_field_list.append(('ln' + str(i + 1), 'rn' + str(i + 1)))
    for i in range(7):
        tu = ('ls' + str(i + 1), 'rs' + str(i + 1))
        user_input_field_list.append(tu)
        expected_filtered_corres_list.append(tu)
    corres_list = get_field_correspondence_list(ltable, rtable, user_input_field_list)
    ltable_col_dict = build_col_name_index_dict(ltable)
    rtable_col_dict = build_col_name_index_dict(rtable)
    filter_corres_list(ltable, rtable, ltable_col_dict, rtable_col_dict, corres_list)
    assert_equal(corres_list, expected_filtered_corres_list)

    ltable_filtered, rtable_filtered = get_filtered_table(ltable, rtable, corres_list)
    feature_list = select_features(ltable_filtered, rtable_filtered)
    assert_equal(feature_list, [1, 4, 7])

    blocker = mg.AttrEquivalenceBlocker()
    cand_set = blocker.block_tables(ltable, rtable, 'ln3', 'rs3')
    assert_equal(debug_blocker(ltable, rtable, cand_set, output_size=10, attr_corres = user_input_field_list).empty, False)
