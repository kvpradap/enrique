from magellan.debugmatcher.debug_booleanrule_matcher import get_feature_name_from_conjunct, get_feature_vector
from magellan.debugmatcher.debug_gui_utils import *
import magellan as mg
from magellan.gui.debug_gui_base import MainWindowManager

def vis_debug_rm(matcher, validation_set, target_attr, feature_table):
    predict_attr_name = get_name_for_predict_column(validation_set.columns)
    predicted = matcher.predict(validation_set, predict_attr_name, append=True, inplace=False)
    eval_summary = mg.eval_matches(predicted, target_attr, predict_attr_name)
    metric = get_metric(eval_summary)
    fp_dataframe = get_dataframe(predicted, eval_summary['false_pos_ls'])
    fn_dataframe = get_dataframe(predicted, eval_summary['false_neg_ls'])
    app = mg._viewapp
    m = MainWindowManager(matcher, "rm", feature_table, metric, predicted, fp_dataframe, fn_dataframe)
    m.show()
    app.exec_()


def vis_tuple_debug_rm_matcher(rm, t1, t2, feature_table):
    # format [True, [False, [[False, conjunct, value], [False, conjunct, value]]]]
    consol_node_list = []
    consol_res = []
    fv = get_feature_vector(t1, t2, feature_table)
    for r_name, conjunct_list in rm.rule_conjunct_list.iteritems():
        res = get_rule_result(rm, t1, t2, conjunct_list, feature_table)
        consol_res.append(res)
        res_ls = [res]
        ls = []
        for conjunct in conjunct_list:
            conj_ls = get_conjunct_result_as_list(rm, t1, t2, conjunct, feature_table, feat_vector=fv)
            ls.append(conj_ls)
        res_ls.append(ls)
        consol_node_list.append(res_ls)

    ret_val = False
    if sum(consol_res) > 0:
        ret_val = True

    return ret_val, consol_node_list
def get_conjunct_result_as_list(rm, t1, t2, conjunct, feat_table, feat_vector):
    # currently I am reusing create_rule function in booleanrulematcher

    cnj_fn, cnj_name, cnj_fn_str = rm.create_rule([conjunct], feat_table, '_temp_')
    res = cnj_fn(t1, t2)
    spacer = '    '
    feat_name = get_feature_name_from_conjunct(conjunct)
    feature_names = list(feat_table['feature_name'])
    ls = []
    if feat_name in feature_names:
        ls = [res, conjunct, feat_vector[feat_name]]
    else:
        ls = [res, conjunct, ""]

    return ls

def get_rule_result(rm, t1, t2, conjunct_list, feature_table):
    if isinstance(conjunct_list, list) == False:
        conjunct_list = [conjunct_list]
    rule_fn, rule_name, rule_fn_str = rm.create_rule(conjunct_list, feature_table, '_temp_')
    res = rule_fn(t1, t2)
    return res
