import pandas as pd
import logging
import datetime
import time

# get the logger from logging module and set the name to current module name
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import magellan as mg


class MTable(pd.DataFrame):
    _metadata = ['properties']
    # ----------------------------------------------------------------------------
    # initialization methods
    def __init__(self, *args, **kwargs):
        key = kwargs.pop('key', None)
        super(MTable, self).__init__(*args, **kwargs)
        self.properties = dict()
        if key is not None:
            self.set_key(key)
        elif mg.__prop__ is not None and mg.__prop__ in self.columns:
            self.set_key(mg.__prop__)
            mg.__prop__ = None
        else:
            self.__key_name__ = get_name_for_key(self.columns)
            self.add_key(self.__key_name__)
            del self.__key_name__




    # based on the documentation at http://pandas.pydata.org/pandas-docs/stable/internals.html
    @property
    def _constructor(self):
        #print self.properties
        mg.__prop__ = None
        if self.get_key() is not None:
            mg.__prop__ = self.get_key()
        return MTable

    def __finalize__(self, other, method=None, **kwargs):
        #print 'Inside finalize' + str(datetime.datetime.now())
        __key_name__ = self.get_key()
        #time.sleep(1)
        if isinstance(other, MTable):
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other, name, None))
        if __key_name__ is not None:
            self.set_key(__key_name__)
        #else:
         #   self.set_key(self.get_key())


        return self

    # ----------------------------------------------------------------------------
    # getters/setters

    def get_key(self):
        return self.get_property('key')

    def set_key(self, key):
        if not isinstance(key, basestring):
            raise TypeError('Input key is expected to be of type string')
        # set the key as index
        #    - It will automatically check for duplicates and null values
        #self.set_index(key, inplace=True, drop=False, verify_integrity=True)
        self.set_property('key', key)

    def get_property(self, key):
        return self.properties.get(key, None)

    def set_property(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError('Input key is expected to be of type string')
        self.properties[key] = value

    # ----------------------------------------------------------------------------
    # add key
    def add_key(self, key):
        if key is None:
            raise AttributeError('Input key is None')
        if key in self.columns:
            # todo: modify the behavior in the following manner
            # - if the key is _m_id and if there is already an _m_id then create a new column with _m_id0
            # - else dont do anything
            logger.warning('Table already contains column with name %s; key not added : %s' %(key,  str(datetime.datetime.now()) ))
            time.sleep(1)

            self.set_key(key)
        else:
            # insert key with numeric values in the first position
            self.insert(0, key, range(0, len(self)))
            self.set_key(key)

#-----------------------
def read_csv(*args, **kwargs):
    if kwargs.has_key('key') is False:
        raise AttributeError('Key is not specified')
    key = kwargs.pop('key', None)
    df = pd.read_csv(*args, **kwargs)
    if key is not None:
        return MTable(df, key=key)
    else:
        df = MTable(df)

        return df

def get_name_for_key(columns):
    k = '_id'
    i = 0
    while True:
        if k not in columns:
            break
        else:
            k = '_id' + str(i)
        i += 1
    return k

def is_key_attr(self, attr_name):
    frame = self.to_dataframe()
    uniq_flag = len(pd.unique(frame[attr_name])) == len(frame)
    nan_flag = sum(frame[attr_name].isnull()) == len(frame)
    return uniq_flag and nan_flag


