import cPickle
import pandas as pd

from magellan.core.mtable import MTable
from magellan.core.pickletable import PickleTable


def read_csv(*args, **kwargs):
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


