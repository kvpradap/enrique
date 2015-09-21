from magellan import MTable
from collections import OrderedDict
import pandas as pd

def evaluate(M, G, label_map, id_map):
    # M - MTable with predicted labels
    # G - MTable with gold label
    # label_map : Tuple with 2 elements; 1st element: label column name in M, 2nd element: label column name in G
    # id_map : List of tuples; each tuple contains 2 elements: 1st element : id column name in M,
    #          2nd element: id column name in G
    if isinstance(M, MTable) is False:
        raise TypeError('Predicted data is not of type MTable')
    if isinstance(G, MTable) is False:
        raise TypeError('Labeled data is not of type MTable')
    m_df = M.to_dataframe()
    g_df = G.to_dataframe()
    m_label = label_map[0]
    g_label = label_map[1]
    m_index = [id_map[0][0], id_map[1][0]]
    g_index = [id_map[0][1], id_map[1][1]]
    m_df = m_df.set_index(m_index, drop=False)
    g_df = g_df.set_index(g_index, drop=False)
    if all([i in m_df.columns for i in m_index]) is False:
        raise AttributeError('Attributes mentioned in id_map do not form a part of first argument')
    if all([i in g_df.columns for i in g_index]) is False:
        raise AttributeError('Attributes mentioned in id_map do not form a part of second argument')
    if m_label not in m_df.columns:
        raise AttributeError('Label column in label_map is not present in columns of first argument')
    if g_label not in g_df.columns:
        raise AttributeError('Label column in label_map is not present in columns of second argument')

    m_idx_vals = m_index.values
    g_idx_vals = g_index.values
    if set(m_idx_vals).issubset(g_idx_vals) is False:
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

