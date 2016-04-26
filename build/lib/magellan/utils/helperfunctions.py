# imports

import logging
import os
import pickle

import jpype
import cloud
import pyximport;

import pandas as pd
from  sklearn.preprocessing import Imputer
pyximport.install()

from magellan.utils import installpath
from magellan import read_csv
from magellan.cython.test_functions import *
from magellan.core.mtable import MTable
from magellan.debugmatcher.debug_gui_utils import get_metric, get_dataframe
# get installation path
def get_install_path():
    plist = installpath.split(os.sep)
    return os.sep.join(plist[0:len(plist)-1])

# initialize JVM
def init_jvm(jvmpath=None):
    """
    Initialize JVM and set class paths to execute sim. functions and tokenizers

    Paramaters
    ----------
    jvmpath : string, defaults to None
        If jvmpath is not given, a default path (identified by jpype package) is used

    Returns
    -------
    status : boolean
        Whether the initialization was successful
    """
    # check if the JVM is already running
    if jpype.isJVMStarted():
        logging.getLogger(__name__).warning('JVM is already running')
        return True

    # prepare classpaths
    # taken from https://github.com/konlpy/konlpy/blob/master/konlpy/jvm.py
    folder_suffix = ['{0}{2}', '{0}{1}secondstring-20120620.jar{2}', \
                     '{0}{1}simfunction.jar{2}', \
                     '{0}{1}simmetrics_jar_v1_6_2_d07_02_07.jar{2}', \
                     '{0}{1}*'
                     ]
    # maps to contents in inst/java under magellan dir
    java_dir = '%s%sinst%sjava' %(get_install_path(), os.sep, os.sep)
    if os.name == 'nt':
        args = [java_dir, os.sep,';']
    else:
        args = [java_dir, os.sep,':']
    classpath = os.sep.join(f.format(*args) for f in folder_suffix)

    # if JVM path is given then use it, else use default JVM path from jpype
    jvmpath = jvmpath or jpype.getDefaultJVMPath()
    if jvmpath:
        jpype.startJVM(jvmpath, '-Djava.class.path=%s' % classpath)
        return True
    else:
        raise ValueError('Please specify JVM path')

# remove non-ascii characters from string
def remove_non_ascii(s):
    s = ''.join(i for i in s if ord(i) < 128)
    s = str(s)
    return str.strip(s)

# find the list difference
def diff(a, b):
  b = set(b)
  return [aa for aa in a if aa not in b]

# helper function to check whether JVM was started
def isJVMStarted():
    return jpype.isJVMStarted()

# load dataset from datasets directory
def load_dataset(filename, key=None):
    p = get_install_path()
    p = os.sep.join([p, 'datasets', filename + '.csv'])
    if filename is 'table_A' or 'table_B':
        key = 'ID'
    df = read_csv(p, key=key)
    return df


# load and save objects
def save_object(obj, file_path):
    """
    Save magellan objects

    Parameters
    ----------
    obj : Python objects. It can be magellan objects such as rule-based blocker, feature table, rule-based matcher,
        match trigger
    file_path : String, file path to store object

    Returns
    -------
    status : boolean, returns True if the command executes successfully.
    """
    with open(file_path, 'w') as f:
        cloud.serialization.cloudpickle.dump(obj, f)
    return True

def load_object(file_path):
    """
    Load magellan objects

    Parameters
    ----------
    file_path : String, file path to load object from

    Returns
    -------
    result : Python object, typically magellan objects such as rule-based blocker, feature table, rule-based matcher,
        match_trigger
    """
    with open(file_path, 'r') as f:
        result = pickle.load(f)
    return result

def create_mtable(table, key=None, ltable=None, rtable=None, foreign_key_ltable=None, foreign_key_rtable=None):
    """
    Create mtable from dataframe
    """
    out_table = MTable(table, key=key)
    truth_vals = [ltable is not None,  rtable is not None,  foreign_key_ltable is not None,
                  foreign_key_rtable is not None]
    if all(truth_vals) == True:
        out_table.set_property('ltable', ltable)
        out_table.set_property('rtable', rtable)
        out_table.set_property('foreign_key_ltable', foreign_key_ltable)
        out_table.set_property('foreign_key_rtable', foreign_key_rtable)
    else:
        if any(truth_vals) == True:
            logging.getLogger(__name__).warning('Not all the properties for vtable are given; so not setting '
                                                'any of them')

    return out_table




def impute_table(table, exclude_attrs=None, missing_val='NaN',
           strategy='mean', axis=0, val_all_nans=0):
    """
    Impute table

    Parameters
    ----------
    table : MTable, for which values should be imputed
    exclude_attrs : list of attribute names to be excluded from imputing.
    missing_val : String, specifies the missing value format.
    strategy : String, on how to impute values. Valid strings: 'mean', 'median', 'most_frequent'
    axis : int, 0/1. axis=1 along rows, and axis=0 along columns.
    val_all_nans: float. Value fto fill in if all the other values are NaN.

    Returns
    -------
    result : Imputed table.
    """

    fv_columns = table.columns
    if exclude_attrs is None:
        feature_names = fv_columns
    else:
        cols = [c not in exclude_attrs for c in fv_columns]
        feature_names = fv_columns[cols]
    # print feature_names
    table = table.copy()
    tbl = table[feature_names]

    t = tbl.values

    imp = Imputer(missing_values=missing_val, strategy=strategy, axis=axis)
    imp.fit(t)
    imp.statistics_[pd.np.isnan(imp.statistics_)] = val_all_nans
    t = imp.transform(t)
    table[feature_names] = t
    return table

def print_eval_summary(eval_summary):
    m = get_metric(eval_summary)
    for key, value in m.iteritems():
        print key + " : " + value


def get_false_positives_as_df(table, eval_summary):
    """
    Get false positives as dataframe

    Parameters
    ----------
    table : MTable, that was used for evaluation or cv
    eval_summary : Dictionary, output from cv['fold_stats'] or eval_matches

    Returns
    -------
    df : Dataframe with false positives
    """
    return get_dataframe(table, eval_summary['false_pos_ls'])


def get_false_negatives_as_df(table, eval_summary):
    """
    Get false negatives as dataframe

    Parameters
    ----------
    table : MTable, that was used for evaluation or cv
    eval_summary : Dictionary, output from cv['fold_stats'] or eval_matches

    Returns
    -------
    df : Dataframe with false negatives
    """
    return get_dataframe(table, eval_summary['false_neg_ls'])

def test_variable():
    x = raw_input('Enter ltable: ')
    print globals()[x]




