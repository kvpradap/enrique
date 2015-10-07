
from magellan.matcher.booleanrulematcher import BooleanRuleMatcher
from magellan.feature.extractfeatures import apply_feat_fns

def debug_booleanrule_matcher(rm, t1, t2, feature_table):
    """
    Debug boolean rule-based matcher

    Parameters
    ----------
    rm : Object of type BooleanRuleMatcher
    t1, t2: pandas Series, tuples that should be used for debugging
    feat_table : pandas dataframe containing feature information
    """
    rule_name = 'Rule_'
    conj_name = 'Conjunct_'
    num_rules = 0
    fv = get_feature_vector(t1, t2, feature_table)
    for r_name, conjunct_list in rm.rule_conjunct_list.iteritems():
        print_rule_result(rm, t1, t2, conjunct_list, feature_table, rule_name+str(num_rules))
        num_rules += 1
        num_conjuncts = 0
        for c in conjunct_list:
            num_conjuncts += 1
            print_conjunct_result(rm, t1, t2, c, feature_table, fv, conj_name+str(num_conjuncts))


def get_feature_vector(t1, t2, feat_table):
    fv = apply_feat_fns(t1, t2, feat_table)
    return fv


def print_conjunct_result(rm, t1, t2, conjunct, feat_table, feat_vector, name):
    # currently I am reusing create_rule function in booleanrulematcher
    cnj_fn, cnj_name, cnj_fn_str = rm.create_rule([conjunct], feat_table, name)
    res = cnj_fn(t1, t2)
    spacer = '    '
    feat_name = get_feature_name_from_conjunct(conjunct)
    feature_names = list(feat_table['feature_name'])
    if feat_name in feature_names:
        print spacer + name + ": " + conjunct + "; Result : " + str(res) + " (value : " + str(feat_vector[feat_name]) + ")"
    else:
        print spacer + name + ": " + conjunct + "; Result : " + str(res)
    return res


def print_rule_result(rm, t1, t2, conjunct_list, feature_table, name):
    if isinstance(conjunct_list, list) is False:
        conjunct_list = [conjunct_list]
    rule_fn, rule_name, rule_fn_str = rm.create_rule(conjunct_list, feature_table, name)
    res = rule_fn(t1, t2)
    spacer = ''
    print spacer + name + " is " + str(res)
    return res


def get_feature_name_from_conjunct(conjunct):
    s = conjunct.split("(") # conjunct is of the form feature(ltuple, rtuple) > 0.7
    if len(s) > 0:
        return s[0].strip()