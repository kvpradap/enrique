import pandas as pd
import logging

# get the logger from logging module and set the name to current module name
logger = logging.getLogger(__name__)

class MTable(pd.DataFrame):
    """ This is a dictionary that can have all kinds of keys that store meta data.
        + key: the name of the key attribute of the table
        + ltable: the name of the left table
        + rtable: the name of the right table
        and any other things that commands may want.

        We assume that the key of a table is just a single attribute (i.e. composite keys are not allowed). This
        is a limitation of current MTable design, made to make key management easier. It may cause some issues
        later. So we need to watch for this and remove this limitation when it becomes too much.
    """
    # set the properties in _metadata
    # Reasons to use _metadata in pandas data frame
    # 1. It is preserved across table manipulations
    # 2. Preserved when the table is pickled
    # 3. Natively supported in pandas

    _metadata = ['properties']
    # ----------------------------------------------------------------------------
    # initialization methods
    def __init__(self, *args, **kwargs):
        key = kwargs.pop('key', None)
        super(MTable, self).__init__(*args, **kwargs)
        self.properties = dict()
        if key is not None:
            self.set_key(key)
        else:
            self.add_key('_m_id')

    # based on the documentation at http://pandas.pydata.org/pandas-docs/stable/internals.html
    @property
    def _constructor(self):
        return MTable

    def __finalize__(self, other, method=None, **kwargs):
        if isinstance(other, MTable):
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other, name, None))
        if self.get_key() not in self.columns:
            self.add_key('_m_id')
        else:
            self.set_key(self.get_key())
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
        self.set_index(key, inplace=True, drop=False, verify_integrity=True)
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
            logger.warning('Table already contains column with name %s; key not added' %key)
            self.set_key(key)
        else:
            # insert key with numeric values in the first position
            self.insert(0, key, range(0, len(self)))
            self.set_key(key)

    # ----------------------------------------------------------------------------
    # I/O methods
    def to_csv(self, *args, **kwargs):
        kwargs['index'] = False
        super(MTable, self).to_csv(*args, **kwargs)

    # ----------------------------------------------------------------------------
    # helper functions
    def to_dataframe(self):
        df = pd.DataFrame(self.values, columns=self.columns)
        if self.get_key() is not None:
            df.set_index(self.get_key(), drop=False, inplace=True)
        df._metadata = ['properties']
        df.properties = self.properties
        return df

    def get_attr_names(self):
        return list(self.columns)



