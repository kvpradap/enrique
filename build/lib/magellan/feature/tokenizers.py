import jpype
import pandas as pd
import pyximport; pyximport.install()

from magellan.cython.test_functions import *
from magellan.utils.helperfunctions import remove_non_ascii

_global_tokenizers = pd.DataFrame({'function_name':['tok_qgram', 'tok_delim'], 'short_name' : ['qgm', 'dlm']})

# Get a list of tokenizers that can be called with just input string as the argument

def get_tokenizers_for_blocking(q = [2, 3], dlm_char = [' ']):
    return get_single_arg_tokenizers(q, dlm_char)

def get_tokenizers_for_matching(q = [2, 3], dlm_char = [' ']):
    return get_single_arg_tokenizers(q, dlm_char)

def get_single_arg_tokenizers(q=[2, 3], dlm_char = [' ']):
    """
    Get a list of tokenizers that can be called with just input string as the argument

    Parameters
    ----------
    q : list of integers, defaults to [2, 3]
        q-value(s) for q-gram tokenizer
    dlm_char : list of strings, defaults to [' ']
        delimiter character used to split strings

    Returns
    -------
    tokenizers : dict, where keys are tokenizer names and values are tokenizer functions
    """
    # return function specific to given q and dlm_char
    qgm_fn_list = [make_tok_qgram(k)for k in q]
    dlm_fn_list = [make_tok_delim(k) for k in dlm_char]

    qgm_names = ['qgm_' + str(x) for x in q]
    dlm_names = ['dlm_dc' + str(i) for i in range(len(dlm_char))]
    names = []
    names.extend(qgm_names)
    names.extend(dlm_names)

    fns = []
    fns.extend(qgm_fn_list)
    fns.extend(dlm_fn_list)

    return dict(zip(names, fns))



# return a delimiter-based tokenizer with a fixed delimiter
def make_tok_delim(d):
    def tok_delim(s):
        # check if the input is of type base string
        if pd.isnull(s):
            return s
        if not isinstance(s, basestring):
            raise ValueError('Input should be of type string')
        s = remove_non_ascii(s)
        return s.split(d)
    return tok_delim

# return a qgram-based tokenizer with a fixed q
def _make_tok_qgram(q):
    def tok_qgram(s):
        # check if the input is of type base string
        if pd.isnull(s):
            return s
        if not isinstance(s, basestring):
            raise ValueError('Input should be of type string')
        if q <= 0:
            raise ValueError('q value must be greater than 0')
        s = remove_non_ascii(s)
        # assume that JVM is already started !!!
        tok_cls = jpype.JClass('build.Tokenizers')
        tokenizer = tok_cls()
        return list(tokenizer.qgramTokenizer(s, float(q))) # fix in java, it should be int
    return tok_qgram

# return a qgram-based tokenizer with a fixed q
def make_tok_qgram(q):
    def tok_qgram(s):
        # check if the input is of type base string
        if pd.isnull(s):
            return s
        if not isinstance(s, basestring):
            raise ValueError('Input should be of type string')
        if q <= 0:
            raise ValueError('q value must be greater than 0')
        return ngrams(s, q)

    return tok_qgram

# q-gram tokenizer
def _tok_qgram(s, q):
    """
    q-gram tokenizer; splits the input string into a list of q-grams

    Parameters
    ----------
    s : string
        source string to be converted into qgrams
    q : integer
        q-value

    Returns
    -------
    qgram_list : list,
         q-gram list of source string
    """
    # check if the input is of type base string
    if pd.isnull(s):
        return s
    if not isinstance(s, basestring):
        raise ValueError('Input should be of type string')
    if q <= 0:
        raise ValueError('q value must be greater than 0')
    s = remove_non_ascii(s)
    # assume that JVM is already started !!!
    tok_cls = jpype.JClass('build.Tokenizers')
    tokenizer = tok_cls()
    return list(tokenizer.qgramTokenizer(s, float(q))) # fix in java, it should be int

# q-gram tokenizer
def tok_qgram(s, q):
    """
    q-gram tokenizer; splits the input string into a list of q-grams

    Parameters
    ----------
    s : string
        source string to be converted into qgrams
    q : integer
        q-value

    Returns
    -------
    qgram_list : list,
         q-gram list of source string
    """
    # check if the input is of type base string
    if pd.isnull(s):
        return s
    if not isinstance(s, basestring):
        raise ValueError('Input should be of type string')
    if q <= 0:
        raise ValueError('q value must be greater than 0')
    return ngrams(s, q)


def tok_delim(s, d):
    """
    delimiter based tokenizer; splits the input string into a list of tokens

    Parameters
    ----------
    s : string
        source string to be converted into qgrams
    d : string
        delimiter

    Returns
    -------
    token_list : list,
         list of tokens
    """

    # check if the input is of type base string
    if pd.isnull(s):
        return s
    if not isinstance(s, basestring):
        raise ValueError('Input should be of type string')
    #s = remove_non_ascii(s)
    return s.split(d)
