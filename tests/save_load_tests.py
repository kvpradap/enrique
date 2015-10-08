from nose.tools import *
import sys
import math
import os
from tests import mg
def test_save_load_ab_blocker():
    filename = '__mg_obj__.pkl'
    ab0 = mg.AttrEquivalenceBlocker()
    mg.save_object(ab0, filename)
    ab1 = mg.load_object(filename)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(type(ab0), type(ab1))

def test_save_load_feature_table():
    #mg.init_jvm()

    filename = '__mg_obj__.pkl'
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    feature_table0 = mg.get_features_for_blocking(A, B)
    mg.save_object(feature_table0, filename)
    feature_table1 = mg.load_object(filename)
    try:
        os.remove(filename)
    except OSError:
        pass
    assert_equal(type(feature_table0), type(feature_table1))
    assert_equal(len(feature_table0), len(feature_table1))
    assert sorted(feature_table0.columns) == sorted(feature_table1.columns)
    ft0_functions = list(feature_table0['function'])
    ft1_functions = list(feature_table1['function'])
    for f0, f1 in zip(ft0_functions, ft1_functions):
        a = f0(A.ix[1], B.ix[2])
        b = f1(A.ix[1], B.ix[2])
        if math.isnan(a) == False and math.isnan(b) == False:
            assert_equal(a, b)
        if math.isnan(a) == True:
            assert_equal(math.isnan(b), True)


def test_save_load_rb_blocker():
    #mg.init_jvm()
    filename = '__mg_obj__.pkl'
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')
    feature_table = mg.get_features_for_blocking(A, B)
    rb0 = mg.RuleBasedBlocker()
    rb0.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) == 1'], feature_table)
    rb0.add_rule(['birth_year_birth_year_anm(ltuple, rtuple) > 0.95',
                  'name_name_mel(ltuple, rtuple)> 0.4'],
                 feature_table)
    C0 = rb0.block_tables(A, B)
    mg.save_object(rb0, filename)
    rb1 = mg.load_object(filename)
    try:
        os.remove(filename)
    except OSError:
        pass

    assert_equal(type(rb0), type(rb1))
    assert_equal(len(rb0.rules), len(rb1.rules))
    assert_equal(len(rb0.rule_source), len(rb1.rule_source))
    assert_equal(rb0.rule_cnt, rb1.rule_cnt)

    C1 = rb1.block_tables(A, B)
    assert_equal(len(C0), len(C1))
    assert_equal(sorted(C0.columns), sorted(C0.columns))


def test_save_load_bb_blocker():
    mg.init_jvm('/Library/Java/JavaVirtualMachines/jdk1.8.0_45.jdk/Contents/Home/jre/lib/server/libjvm.dylib')
    from magellan.feature.simfunctions import jaccard
    from magellan.feature.tokenizers import tok_qgram
    def block_fn_1(ltuple, rtuple):
        val = jaccard(tok_qgram(ltuple['address'], 3), tok_qgram(rtuple['address'], 3))
        if  val < 0.4:
            return True
        else:
            return False
    bb0 = mg.BlackBoxBlocker()
    bb0.set_black_box_function(block_fn_1)
    filename = '__mg_obj__.pkl'
    A = mg.load_dataset('table_A')
    B = mg.load_dataset('table_B')

    C0 = bb0.block_tables(A, B)
    mg.save_object(bb0, filename)
    bb1 = mg.load_object(filename)
    try:
        os.remove(filename)
    except OSError:
        pass

    assert_equal(type(bb0), type(bb1))
    C1 = bb1.block_tables(A, B)
    assert_equal(len(C0), len(C1))
    assert_equal(sorted(C0.columns), sorted(C0.columns))









