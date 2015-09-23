import cPickle
import pandas as pd
import logging

from magellan.core.mtable import MTable
from magellan.core.pickletable import PickleTable


def read_csv_(*args, **kwargs):
    """
    Read CSV (comma-separated) file into MTable

    Parameters
    ----------
    args : arguments to pandas read_csv command
    kwargs : arguments to pandas read_csv command along with optional "key" parameter.
        If key parameter is given, then it will be set as key,  else a new attribute ("_id")
        is added and set as key

    Returns
    -------
    result : MTable
    """
    if kwargs.has_key('key') is False:
        raise AttributeError('Key is not specified')
    key = kwargs.pop('key', None)
    df = pd.read_csv(*args, **kwargs)
    if key is not None:
        return MTable(df, key=key)
    else:
        df = MTable(df)
        #key_name=df._get_name_for_key(df.columns)
        #df.add_key(key_name)
        return df



def read_csv(file_path, **kwargs):
    properties = get_properties_from_file(file_path)
    properties = update_properties(properties, **kwargs)


def load_table(path):
    """
    Load picked MTable object from the specified file path

    Parameters
    ----------
    path : string
        File path

    Returns
    -------
    unpickled : MTable object stored in file

    Notes
    -----
    Internally the function calls pandas.to_pickle command
    """
    filename = open(path, 'r')
    obj = cPickle.load(filename)
    table = obj.table
    properties = obj.properties
    table.properties = properties
    if obj.ltable_properties is not None:
        ltable = table.get_property('ltable')
        ltable.properties = obj.ltable_properties
        table.set_property('ltable', ltable)
    if obj.rtable_properties is not None:
        rtable = table.get_property('rtable')
        rtable.properties = obj.rtable_properties
        table.set_property('rtable', rtable)
    return table



def get_properties_from_file(file_path):
    properties = dict()
    num_lines = 0
    with open(file_path) as f:
        stop_flag = False
        while stop_flag is False:
            line = next(f)
            if line.startswith('#'):
                line = line.lstrip('#')
                tokens = line.split(':')
                assert len(tokens) is 2, "Error in file, the num tokens is not 2"
                key = tokens[0].strip()
                value = tokens[1].strip()
                if value is not "POINTER":
                    properties[key] = value
                num_lines += 1

            else:
                stop_flag = True
    return properties, num_lines


def update_properties(properties, input):

    # first update
    for k in properties.keys():
        if input.has_key(k):
            value = input.pop(k)
            if value is not None:
                properties[k] = value
            else:
                logging.getLogger(__name__).warning('%s key had a value in file but input arg is set to None')
                v = properties.pop(k) # remove the key-value pair

    # Now add
    # following are the list of properties that the user can provide
    mtable_props = ['key', 'ltable', 'rtable', 'foreign_key_ltable', 'foreign_key_rtable']

    # add based on what the user can give as key value argument

    # add another function to check properties.



    # vtable_flag = any(x in vtable_props for x in properties)
    # if vtable_flag is True
