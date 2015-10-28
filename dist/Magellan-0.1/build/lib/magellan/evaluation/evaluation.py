from magellan import MTable
from collections import OrderedDict
import pandas as pd

def evaluate(M, G, label_map, id_map):
    # M - MTable with predicted labels
    # G - MTable with gold label
    # label_map : Tuple with 2 elements; 1st element: label column name in M, 2nd element: label column name in G
    # id_map : List of tuples; each tuple contains 2 elements: 1st element : id column name in M,
    #          2nd element: id column name in G
    if isinstance(M, MTable) == False:
        raise TypeError('Predicted data is not of type MTable')
    if isinstance(G, MTable) == False:
        raise TypeError('Labeled data is not of type MTable')
    m_df = M.to_dataframe()
    g_df = G.to_dataframe()
    m_label = label_map[0]
    g_label = label_map[1]
    m_index = [id_map[0][0], id_map[1][0]]
    g_index = [id_map[0][1], id_map[1][1]]
    m_df = m_df.set_index(m_index, drop=False)
    g_df = g_df.set_index(g_index, drop=False)
    if all([i in m_df.columns for i in m_index]) == False:
        raise AttributeError('Attributes mentioned in id_map do not form a part of first argument')
    if all([i in g_df.columns for i in g_index]) == False:
        raise AttributeError('Attributes mentioned in id_map do not form a part of second argument')
    if m_label not in m_df.columns:
        raise AttributeError('Label column in label_map is not present in columns of first argument')
    if g_label not in g_df.columns:
        raise AttributeError('Label column in label_map is not present in columns of second argument')

    m_idx_vals = m_index.values
    g_idx_vals = g_index.values
    if set(m_idx_vals).issubset(g_idx_vals) == False:
        raise AssertionError('Table with predicted labels donot form a subset of the table with actual labels')
    pm = 0.0 # predicted match (i.e 1)
    cm = 0.0 # correct match (i.e 1)
    gm = 0.0 # actual match (i.e 1)

    false_pos = []
    false_neg = []
    for m in m_idx_vals:
        lbl_m = m_df.ix[m, m_label]
        lbl_g = g_df.ix[m, g_label]
        if lbl_m == 1:
            pm += 1
            if lbl_g == 1:
                cm +=1
        if lbl_g == 1:
            gm += 1

        # false positive
        if lbl_m == 1 and lbl_g == 0:
            d = dict(zip(m_index, m))
            false_pos.append(d)
        # false negative
        if lbl_m == 0 and lbl_g == 1:
            d = dict(zip(m_index, m))
            false_neg.append(d)
    precision = cm/pm
    recall = cm/gm
    if precision == 0.0 and recall == 0.0:
        f1 = 0.0
    else:
        f1 = (2.0*precision*recall)/(precision + recall)

    fp_df = pd.DataFrame(false_pos)
    fn_df = pd.DataFrame(false_neg)

    out_dict = OrderedDict()
    out_dict['precision'] = precision
    out_dict['recall'] = recall
    out_dict['f1'] = f1
    out_dict['false_positives'] = fp_df
    out_dict['false_negatives'] = fn_df

    return out_dict

def eval_matches(X, gold_label_attr, predicted_label_attr):
    """
    Evaluate matches

    Parameters
    ----------
    X : MTable, containing both the 'True' labels and predicted labels
    gold_label_attr : String, column name containing True labels
    predicted_label_attr : String, column name containing predicted labels

    Returns
    -------
    eval_summary : Python dictionary containing the following key-value pairs:

    prec_numerator : int, numerator for precision value computation (i.e the number of true positives)
    prec_denominator : int, denominator for precision value computation (i.e. tp + fp)
    precision : float, precision
    recall_numerator : int, numerator for  recall value computation (i.e the number of true positives)
    recall_denominator : int, denominator for recall value computation (i.e. tp + fn)
    recall : float, recall
    f1 : float, f1 value
    pred_pos_num : int, number of predicted postives (i.e matches)
    false_pos_num : int, number of false positives
    false_pos_ls : List of tuples. Each tuple is a false positive pair containing ltable id, rtable id.
    pred_neg_num : int, number of predicted negatives (i.e non-matches)
    false_neg_num : int, number of false negatives
    false_neg_ls : List of tuples. Each tuple is a false negative pair containing ltable id, rtable id.

    """

    Y = X.reset_index(drop=False, inplace=False)
    g = Y[gold_label_attr]
    if isinstance(g, pd.DataFrame):
        g = g.T
        assert len(g) == 1, 'Error: Column is picked as dataframe and the num rows > 1'
        g = g.iloc[0]



    p = Y[predicted_label_attr]
    if isinstance(p, pd.DataFrame):
        p = p.T
        assert len(p) == 1, 'Error: Column is picked as dataframe and the num rows > 1'
        p = p.iloc[0]


    # get false label (0) indices
    gf = g[g == 0].index.values

    pf = p[p == 0].index.values

    # get true label (1) indices
    gt = g[g == 1].index.values

    pt = p[p == 1].index.values


    # get false positive indices
    fp_indices = list(set(gf).intersection(pt))

    # get true positive indices
    tp_indices = list(set(gt).intersection(pt))


    # get false negative indices
    fn_indices = list(set(gt).intersection(pf))


    # get true negative indices
    tn_indices = list(set(gf).intersection(pf))

    n_tp = float(len(tp_indices))
    n_fp = float(len(fp_indices))
    n_fn = float(len(fn_indices))
    n_tn = float(len(tn_indices))
    prec_num = n_tp
    prec_den = n_tp + n_fp
    rec_num = n_tp
    rec_den = n_tp + n_fn
    precision = prec_num/prec_den
    recall = rec_num/rec_den

    if precision == 0.0 and recall == 0.0:
        f1 = 0.0
    else:
        f1 = (2.0*precision*recall)/(precision + recall)


    l_key = X.get_property('foreign_key_ltable')
    r_key = X.get_property('foreign_key_rtable')
    Y.set_index([l_key, r_key], drop=False, inplace=True)
    false_pos_ls = list(Y.ix[fp_indices].index.values)
    false_neg_ls = list(Y.ix[fn_indices].index.values)
    ret_dict = OrderedDict()
    ret_dict['prec_numerator'] = prec_num
    ret_dict['prec_denominator'] = prec_den
    ret_dict['precision'] = precision
    ret_dict['recall_numerator'] = rec_num
    ret_dict['recall_denominator'] = rec_den
    ret_dict['recall'] = recall
    ret_dict['f1'] = f1
    ret_dict['pred_pos_num'] = n_tp + n_fp
    ret_dict['false_pos_num'] = n_fp
    ret_dict['false_pos_ls'] = false_pos_ls
    ret_dict['pred_neg_num'] = n_fn + n_tn
    ret_dict['false_neg_num'] = n_fn
    ret_dict['false_neg_ls'] = false_neg_ls
    return ret_dict



