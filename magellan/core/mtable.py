import cPickle
import pandas as pd
import logging

from magellan.core.pickletable import PickleTable

# get the logger from logging module and set the name to current module name
logger = logging.getLogger(__name__)

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
        else:
            key_name = self._get_name_for_key(self.columns)
            self.add_key(key_name)

    # get the name for key attribute.
    def _get_name_for_key(self, columns):
        k = '_id'
        i = 0
        # try attribute name of the form "_id", "_id0", "_id1", ... and
        # return the first available name
        while True:
            if k not in columns:
                break
            else:
               k = '_id' + str(i)
            i += 1
        return k

    # based on the documentation at http://pandas.pydata.org/pandas-docs/stable/internals.html
    # @property
    # def _constructor(self):
    #      return MTable

    # def __finalize__(self, other, method=None, **kwargs):
    #     #print 'calling finalize'
    #     # copy the attributes from older mtable to new mtable
    #     if isinstance(other, MTable):
    #         for name in self._metadata:
    #             object.__setattr__(self, name, getattr(other, name, None))
    #     return self

    # ----------------------------------------------------------------------------
    # getters/setters

    def get_key(self):
        """
        Return name of key attribute
        """
        return self.get_property('key')

    def set_key(self, key):
        """
        Set the key attribute

        Parameters
        ----------
        key : string, name of the key attribute

        Returns
        -------
        status : boolean
            Whether the function successfully set the key

        Notes
        -----
        Key attribute is expected to satisfy the following properties
        * do not contain duplicate values
        * do not contain null values
        """
        if not isinstance(key, basestring):
            raise TypeError('Input key is expected to be of type string')
        if self.is_key_attr(key) is False:
            raise KeyError('Input attribute does not satisfy requirements for a key')
        else:
            self.set_property('key', key)

    def get_property(self, prop_name):
        """
        Get the value for a property

        Parameters
        ----------
        prop_name : string, name of the property that is queried for

        Returns
        -------
        property : object
            Value set for the property
        """
        return self.properties.get(prop_name, None)

    def set_property(self, prop_name, value):
        """
        Set the value for a property

        Parameters
        ----------
        prop_name : string, name of the property for which value to be set
        value : object, value for the property

        Returns
        -------
        status : boolean
         Whether the function successfully set the attribute
        """

        if not isinstance(prop_name, basestring):
            raise TypeError('Input key is expected to be of type string')
        self.properties[prop_name] = value

    # ----------------------------------------------------------------------------
    # add key
    def add_key(self, key):
        """
        Add a key attribute to MTable

        Parameters
        ----------
        key : string, name of the attribute to be added as key to MTable

        Returns
        -------
        status : boolean
            Whether the function successfully added the key to MTable

        """
        if key is None:
            raise AttributeError('Input key is None')
        if key in self.columns:
            logger.warning('Table already contains column with name %s; key not added' %key)
        else:
            self.insert(0, key, range(0, len(self)))
            self.set_key(key)


    # ----------------------------------------------------------------------------
    # helper functions
    def to_dataframe(self):
        """
        Convert MTable to pandas Dataframe

        Returns
        -------
        df : pandas.Dataframe

        Notes
        -----
        MTable's metadata is not copied to returned dataframe
        """
        copy_dtype = dict(zip(self.columns, self.dtypes))

        df = pd.DataFrame(self.values, columns=self.columns)
        # set the dtypes in dataframe as the same dtype in MTable
        for c in df.columns:
            df[c] = df[c].astype(copy_dtype[c])

        return df

    def get_attr_names(self):
        """
        Get the attribute names in a MTable

        Returns
        -------
        attr_names : list
            List of attribute names in MTable
        """
        return list(self.columns)

    def save_table(self, path):
        """
        Pickle object to input file path

        Parameters
        ----------
        path : string
            File path

        Returns
        -------
        status : boolean
            Whether the function successfully saved the table

        """
        filename = file(path, 'w')
        obj = PickleTable(self, self.properties)
        cPickle.dump(obj, filename)



    # check whether an attribute can be set as key
    def is_key_attr(self, attr_name):
        #print attr_name
        uniq_flag = len(self[attr_name]) == len(self)
        nan_flag = sum(self[attr_name].isnull()) == 0
        return uniq_flag and nan_flag



