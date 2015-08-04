import pandas as pd
import magellan as mg
import logging

# get features where all inputs required for the function is given
def get_features(ltable, rtable, l_attr_types, r_attr_types, attr_corres, tok, sim_funcs):
    """
    Generate features from input tables

    Parameters
    ----------
    ltable, rtable : MTable,
        Input tables for which features have to be generated
    l_attr_types, r_attr_types : dict
        Dictionary containing attribute types (also see: mg.get_attr_types)
    attr_corres : dict
        Contains attribute correspondence between two tables (also see: mg.get_attr_corres)
    tok : dict
        Contains tokenizers, where key is tokenizer name and value is function object
        (also see: mg.get_single_argument_tokenizers)
    sim_funcs : dict
        Contains similarity functions, where key is similarity function name and value is function object

    Returns
    -------
    feature_table : pandas DataFrame
        Consists of following columns
        * feature_name  - string, feature name
        * left_attribute - string, attribute name
        * right_attribute - string, attribute name
        * left_attr_tokenizer - string, tokenizer name
        * right_attr_tokenizer - string, tokenizer name
        * simfunction - string, sumilarity function name
        * function - function object
        * function_source - string, containing source code


    """

    # check whether the order of input table matches with table mentioned in l_attr_types, r_attr_type and attr_corres
    if check_table_order(ltable, rtable, l_attr_types, r_attr_types, attr_corres) is False:
        raise AssertionError('Table order is different than what is mentioned in l/r_attr_types and attr_corres')

    # initialize output feature dictionary list
    feat_dict_list = []

    # generate features for each attribute correspondence
    for attrs in attr_corres['corres']:
        l_attr_type = l_attr_types[attrs[0]]
        r_attr_type = r_attr_types[attrs[1]]
        if l_attr_type != r_attr_type:
            logging.getLogger(__name__).warning('%s type and %s type are different' %attrs)
            continue
        feats = get_features_for_type(l_attr_type)
        # convert features to function objects
        fn_objs = conv_func_objs(feats, attrs, tok, sim_funcs)
        feat_dict_list.append(fn_objs)

    # convert the list of (feature) dictionaries to dataframe
    df = pd.DataFrame(flatten_list(feat_dict_list))

    df = df[['feature_name', 'left_attribute', 'right_attribute', 'left_attr_tokenizer', 'right_attr_tokenizer', 'simfunction', 'function', 'function_source']]
    return df

# check whether the order of tables matches with what is mentioned in  l_attr_types, r_attr_type and attr_corres
def check_table_order(ltable, rtable, l_attr_types, r_attr_types, attr_corres):
    # get the ids
    l_id = id(ltable)
    r_id = id(rtable)

    # check whether ltable id matches with id of table mentioned in l_attr_types
    if l_id != id(l_attr_types['_m_table']):
        logging.getLogger(__name__).error('ltable is not the same as table mentioned in left attr types')
        return False

    # check whether rtable id matches with id of table mentioned in r_attr_types
    if r_id != id(r_attr_types['_m_table']):
        logging.getLogger(__name__).error('rtable is not the same as table mentioned in right attr types')
        return False

    # check whether ltable matches with ltable mentioned in attr_corres
    if l_id != id(attr_corres['ltable']):
        logging.getLogger(__name__).error('ltable is not the same as table mentioned in attr correspondence')
        return False

    # check whether rtable matches with rtable mentioned in attr_corres
    if r_id != id(attr_corres['rtable']):
        logging.getLogger(__name__).error('rtable is not the same as table mentioned in attr correspondence')
        return False

# get look up table to generate features
def get_feat_lkp_tbl():
    lkp_tbl = dict()

    # THE FOLLOWING MUST BE MODIFIED
    # features for type str_eq_1w
    lkp_tbl['STR_EQ_1W'] = [('lev')]

    # features for type str_bt_1w_5w
    lkp_tbl['STR_BT_1W_5W'] = [('jaccard', 'qgm_3', 'qgm_3'),
                               ('jaccard', 'qgm_2', 'qgm_3')]

    # features for type str_bt_5w_10w
    lkp_tbl['STR_BT_5W_10W'] = [('jaccard', 'qgm_3', 'qgm_3')]

    # features for type str_gt_10w
    lkp_tbl['STR_GT_10W'] = [('jaccard', 'qgm_3', 'qgm_3')]

    # features for NUMERIC type
    lkp_tbl['NUM'] = [('rel_diff')]

    # features for BOOLEAN type
    lkp_tbl['BOOL'] = [('exact_match')]

    return lkp_tbl

# get features to be generated for a type
def get_features_for_type(t):
    lkp_tbl = get_feat_lkp_tbl()
    if t is 'str_eq_1w':
        rec_fns = lkp_tbl['STR_EQ_1W']
    elif t is 'str_bt_1w_5w':
        rec_fns = lkp_tbl['STR_BT_1W_5W']
    elif t is 'str_bt_5w_10w':
        rec_fns = lkp_tbl['STR_BT_5W_10W']
    elif t is 'str_gt_10w':
        rec_fns = lkp_tbl['STR_GT_10W']
    elif t is 'numeric':
        rec_fns = lkp_tbl['NUM']
    elif t is 'boolean':
        rec_fns = lkp_tbl['BOOL']
    else:
        raise TypeError('Unknown type')
    return rec_fns

# convert features from look up table to function objects
def conv_func_objs(feats, attrs, tok, sim_funcs):
    tok_list = tok.keys()
    sim_list = sim_funcs.keys()
    valid_list = [check_valid_tok_sim(i, tok_list, sim_list) for i in feats]
    # get function as a string and other meta data; finally we will get a list of tuples
    func_tuples = [get_fn_str(inp, attrs) for inp in valid_list]
    func_objs = conv_fn_str_to_obj(func_tuples)
    return func_objs


# check whether tokenizers and simfunctions are allowed
# inp is of the form ('jaccard', 'qgm_3', 'qgm_3') or ('lev')
def check_valid_tok_sim(inp, simlist, toklist):
    if isinstance(inp, basestring):
        inp = [inp]
    assert len(inp) == 1 or len(inp) == 3, 'len of feature config should be 1 or 3'
    # check whether the sim function in features is in simlist
    if len(set(inp).intersection(simlist)) > 0:
        return inp
    # check whether the tokenizer in features is in tok list
    if len(set(inp).intersection(toklist)) > 0:
        return inp
    return None

# get function string for a feature
def get_fn_str(inp, attrs):
    if inp:
        args = []
        args.extend(attrs)
        if isinstance(inp, basestring):
            inp = [inp]
        else:
            args.extend(inp)
        # fill function string from a template
        return fill_fn_template(*args)
    else:
        return None

# fill function template
def fill_fn_template(attr1, attr2, sim_func, tok_func_1=None, tok_func_2=None):
    # construct function string
    s = 'from magellan.feature.simfunctions import *\nfrom magellan.feature.tokenizers import *\n'
    # get the function name
    fn_name = get_fn_name(attr1, attr2, sim_func, tok_func_1, tok_func_2)
    # proceed with function construction
    fn_st = 'def ' + fn_name + '(ltuple, rtuple):'
    s += fn_st
    s += '\n'

    # add 4 spaces
    s += '    '
    fn_body = 'return '
    if tok_func_1 is not None and tok_func_2 is not None:
        fn_body = fn_body + sim_func+'(' + tok_func_1 + '(' + 'ltuple["' + attr1 + '"]'
        fn_body += '), '
        fn_body = fn_body + tok_func_2 + '(' + 'rtuple["' + attr2 + '"]'
        fn_body = fn_body + ')) '
    else:
        fn_body = fn_body + sim_func + '(' + 'ltuple["' + attr1 +'"], rtuple["' + attr2 + '"])'
    s += fn_body

    return fn_name, attr1, attr2, tok_func_1, tok_func_2, sim_func, s

# construct function name from attrs, tokenizers and sim funcs
def get_fn_name(attr1, attr2, sim_func, tok_func_1=None, tok_func_2=None):
    fp = '_'.join([attr1, attr2])
    name_lkp = dict()
    name_lkp["jaccard"] = "jac"
    name_lkp["tok_whitespace"] = "ws"
    name_lkp["tok_qgram"] = "qgm"
    name_lkp["lev"] = "lev"
    name_lkp["cosine"] = "cos"
    name_lkp["monge_elkan"] = "mel"
    name_lkp["needleman_wunsch"] = "nmw"
    name_lkp["smith_waterman"] = "sw"
    name_lkp["smith_waterman_gotoh"] = "swg"
    name_lkp["jaro"] = "jar"
    name_lkp["jaro_winkler"] = "jwn"
    name_lkp["soundex"] = "sdx"
    name_lkp["exact_match"] = "exm"
    name_lkp["abs_diff"] = "adf"
    name_lkp["rel_diff"] = "rdf"
    name_lkp["1"] = "1"
    name_lkp["2"] = "2"
    name_lkp["3"] = "3"
    name_lkp["4"] = "4"
    arg_list = [sim_func, tok_func_1, tok_func_2]
    nm_list = [name_lkp.get(tok, tok) for tok in arg_list if tok]
    sp = '_'.join(nm_list)
    return '_'.join([fp, sp])

# conv function string to function object and return with meta data
def conv_fn_str_to_obj(fn_tup):
    d_orig = {}
    d_ret_list = []
    for f in fn_tup:
        d_ret = {}
        name = f[0]
        attr1 = f[1]
        attr2 = f[2]
        tok_1 = f[3]
        tok_2 = f[4]
        simfunction = f[5]
        exec f[6] in d_orig
        d_ret['function'] = d_orig[name]
        d_ret['feature_name'] = name
        d_ret['left_attribute'] = attr1
        d_ret['right_attribute'] = attr2
        d_ret['left_attr_tokenizer'] = tok_1
        d_ret['right_attr_tokenizer'] = tok_2
        d_ret['simfunction'] = simfunction
        d_ret['function_source'] = f[6]


        d_ret_list.append(d_ret)
    return d_ret_list

def flatten_list(inp_list):
    return [item for sublist in inp_list for item in sublist]

# get features for a lay user
def get_features_for_blocking(A, B):
    """
    Get features with minimal input

    Parameters
    ----------
    A, B : MTable,
        Input tables

    Returns
    -------
    feature_table : pandas DataFrame
        Consists of following columns
        * feature_name  - string, feature name
        * left_attribute - string, attribute name
        * right_attribute - string, attribute name
        * left_attr_tokenizer - string, tokenizer name
        * right_attr_tokenizer - string, tokenizer name
        * simfunction - string, sumilarity function name
        * function - function object
        * function_source - string, containing source code
    """
    sim = mg.get_sim_funs()
    tok = mg.get_single_arg_tokenizers()
    t_A = mg.get_attr_types(A)
    t_B = mg.get_attr_types(B)
    attr_corres = mg.get_attr_corres(A, B)
    feat_table = get_features(A, B, t_A, t_B, attr_corres, tok, sim)
    return feat_table