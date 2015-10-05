# imports

import jpype
import logging
import os
import cloud
import pickle

from magellan.utils import installpath
from magellan import read_csv_
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
    df = read_csv_(p, key=key)
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
        cloud.serialization.cloudpicke.dump(obj, f)
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






