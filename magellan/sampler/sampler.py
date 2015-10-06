import math
import numpy as np
import sys
from magellan.core.mtable import MTable

def _get_stop_words():
    stop_words = [
                "a", "about", "above",
                "across", "after", "afterwards", "again", "against", "all", "almost",
                "alone", "along", "already", "also","although","always","am","among",
                "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow",
                "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at",
                "back","be","became", "because", "become", "becomes", "becoming", "been",
                "before", "beforehand", "behind", "being", "below", "beside", "besides",
                "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can",
                "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe",
                "detail", "do", "done", "down", "due", "during", "each", "eg", "eight",
                "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even",
                "ever", "every", "everyone", "everything", "everywhere", "except", "few",
                "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former",
                "formerly", "forty", "found", "four", "from", "front", "full", "further",
                "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her",
                "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself",
                "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in",
                "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep",
                "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may",
                "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most",
                "mostly", "move", "much", "must", "my", "myself", "name", "namely",
                "neither", "never", "nevertheless", "next", "nine", "no", "nobody",
                "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off",
                "often", "on", "once", "one", "only", "onto", "or", "other", "others",
                "otherwise", "our", "ours", "ourselves", "out", "over", "own","part",
                "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem",
                "seemed", "seeming", "seems", "serious", "several", "she", "should",
                "show", "side", "since", "sincere", "six", "sixty", "so", "some",
                "somehow", "someone", "something", "sometime", "sometimes", "somewhere",
                "still", "such", "system", "take", "ten", "than", "that", "the", "their",
                "them", "themselves", "then", "thence", "there", "thereafter", "thereby",
                "therefore", "therein", "thereupon", "these", "they", "thickv", "thin",
                "third", "this", "those", "though", "three", "through", "throughout",
                "thru", "thus", "to", "together", "too", "top", "toward", "towards",
                "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
                "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
                "whence", "whenever", "where", "whereafter", "whereas", "whereby",
                "wherein", "whereupon", "wherever", "whether", "which", "while",
                "whither", "who", "whoever", "whole", "whom", "whose", "why", "will",
                "with", "within", "without", "would", "yet", "you", "your", "yours",
                "yourself", "yourselves"
    ]
    return stop_words

# order tables such that small table is in the left
def _order_tables(ltable, rtable):
    if len(rtable) <= len(ltable):
        return rtable, ltable, True
    else:
        return ltable, rtable, False

# get string columns
def _get_str_cols(table):
    cols = list(table.columns[table.dtypes==object])
    return cols

# create inverted index from token to position
def _inv_index(table):
    stop_words = set(_get_stop_words())
    str_cols = _get_str_cols(table)
    n = len(table)
    key_pos = dict(zip(range(n), range(n)))
    inv_index = dict()
    pos = 0
    for k, v in table.iterrows():
        # get values from string columns
        val = v[str_cols]
        # concatenate them
        s = ' '.join(val).lower()
        # tokenize them
        s = set(s.split())
        s = s.difference(stop_words)
        for token in s:
            lst = inv_index.get(token, None)
            if lst is None:
                inv_index[token] = [pos]
            else:
                lst.append(pos)
                inv_index[token] = lst
        pos += 1
    return inv_index


def _probe_index(b_table, y, s_tbl_sz, s_inv_index):
    y_pos = math.floor(y/2)
    h_table = set()
    stop_words = set(_get_stop_words())
    str_cols = _get_str_cols(b_table)
    for k, v in b_table.iterrows():
        val = v[str_cols]
        s = set(' '.join(val).lower().split())
        s = s.difference(stop_words)
        m = set()
        for token in s:
            ids = s_inv_index.get(token, None)
            if ids is not None:
                m.update(ids)
        # pick y/2 elements from m
        k = min(y_pos, len(m))
        m = list(m)
        smpl_pos = np.random.choice(m, k, replace=False)
        s_pos_set = set()
        s_pos_set.update(smpl_pos)
        s_tbl_ids = set(range(s_tbl_sz))
        rem_locs = list(s_tbl_ids.difference(s_pos_set))
        if y - k > 0:
            s_neg_set = np.random.choice(rem_locs, y - k, replace=False)
            h_table.update(s_pos_set, s_neg_set)
    return h_table

# down sample two tables : based on sanjib's index based solution
def down_sample(ltable, rtable, size, y):
    s_table, b_table, is_swapped = _order_tables(ltable, rtable)
    s_inv_index = _inv_index(s_table)
    b_sample_size = min(math.floor(size/y), len(b_table))
    b_tbl_indices = np.random.choice(len(b_table), b_sample_size, replace=False)
    s_tbl_indices = _probe_index(b_table.ix[b_tbl_indices], y,
                                 len(s_table), s_inv_index)
    if is_swapped:
        s_tbl_indices, b_tbl_indices = b_tbl_indices, s_tbl_indices
    l_sampled = MTable(ltable.iloc[list(s_tbl_indices)], ltable.get_key())
    l_sampled.properties = ltable.properties
    r_sampled = MTable(rtable.iloc[list(b_tbl_indices)], rtable.get_key())
    r_sampled.properties = rtable.properties
    return l_sampled, r_sampled

# sample one table using random sampling
def sample_table(table, size, replace=False):
    s_indices = np.random.choice(len(table), size, replace=replace)
    # sort the indices - just to have an order
    s_indices = sorted(s_indices)
    sampled_table =  table.iloc[list(s_indices)]
    #print sampled_table.properties
    sampled_table = MTable(sampled_table, key=table.get_key())
    sampled_table.properties = table.properties
    return sampled_table
