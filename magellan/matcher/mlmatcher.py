import pandas as pd
import magellan as mg
import numpy as np

from sklearn.preprocessing import Imputer
from magellan.matcher.matcher import Matcher

class MLMatcher(Matcher):
    # -----------------------------------------------------------
    # fit routines
    def fit_sklearn(self, x, y, check_rem=True):

        # get the data in a format that sklearn can operate on
        x, y = self.get_data_for_sklearn(x, y, check_rem=check_rem)
        # fit
        self.clf.fit(x, y)
        return True

    def fit_ex_attrs(self, table, exclude_attrs, target_attr):
        # assume the exclude attrs and target attr is present
        if not isinstance(exclude_attrs, list):
            exclude_attrs = [exclude_attrs]
        attrs_to_project = mg.diff(table.columns, exclude_attrs)
        table = table.to_dataframe()
        x = table[attrs_to_project]
        #print attrs_to_project
        y = table[target_attr]
        self.fit_sklearn(x, y, check_rem=False)

    def fit(self, x=None, y=None, table=None, exclude_attrs=None, target_attr=None):

        """
        Fit model based on training data

        Parameters
        ----------
        table : MTable, defaults to None
            of feature vectors and user included attributes

        x : MTable, defaults to None
            of feature vectors

        y : MTable, defaults to None
            of labels

        exclude_attrs: list,
            list of attributes to be excluded in 'table'

        target_attr : string,
            target attribute name containing labels


        Returns
        -------
        model : object
            trained classifier model

        """
        if x is not None and y is not None:
            self.fit_sklearn(x, y)
        elif (table is not None and exclude_attrs is not None) and target_attr is not None:
            self.fit_ex_attrs(table, exclude_attrs, target_attr)
            #print 'After fitting'
        else:
            raise SyntaxError('The arguments supplied does not match the signatures supported !!!')

    # -----------------------------------------------------------
    # predict routines

    # call predict method of sklearn classifier

    def predict_sklearn(self, x, check_rem=True):

        # Note: here check_rem is just passing what is coming in i.e it can be true or false based up on who is calling
        # it
        x = self.get_data_for_sklearn(x, check_rem=check_rem)
        y =  self.clf.predict(x)
        return y

    # variant of predict method, where data is derived based on exclude attributes

    def predict_ex_attrs(self, table, exclude_attrs):
        if not isinstance(exclude_attrs, list):
            exclude_attrs = [exclude_attrs]
        table = table.to_dataframe()
        attrs_to_project = mg.diff(table.columns, exclude_attrs)
        x = table[attrs_to_project]
        y = self.predict_sklearn(x, check_rem=False)
        return y


    # predict method
    def predict(self, x=None, table=None, exclude_attrs=None, target_attr=None, append=False):
        """
        Predict 'matches' on a MTable of feature vectors

        Parameters
        ----------
        table : MTable, defaults to None
            of feature vectors and user included attributes

        x : MTable, defaults to None
            of feature vectors

        exclude_attrs: list,
            list of attributes to be excluded in 'table'

        target_attr : string,
            target attribute name to be appended to 'table' containing predicted labels

        append : boolean,
            Whether the output should be appended

        Returns
        -------
        The function can return either an array or MTable.

        It will return an array of predicted labels when append is false

        It will return a MTable with predicted labels appended when all the following condns are satisfied

        * table is not None
        * target_attr is not None
        * append is True

        """
        if x is not None:
            y = self.predict_sklearn(x)
            if table is not None and target_attr is not None and append is True:
                table[target_attr] = y
                return table
        elif table is not None and exclude_attrs is not None:
            y = self.predict_ex_attrs(table, exclude_attrs)
            if target_attr is not None and append is True:
                table[target_attr] = y
                return table
        else:
            raise SyntaxError('The arguments supplied does not match the signatures supported !!!')
        return y

    # get and set name of matcher
    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    # -----------------------------------------------------------
    # common routines

    def get_data_for_sklearn(self, x, y=None, check_rem=True):
        # check to see if we have to remove id column
        if x.columns[0] is '_id' and check_rem is True:
            x = x.values
            x = np.delete(x, 0, 1)
        else:
            x = x.values
        if y is not None:
            if not isinstance(y, pd.Series) and y.columns[0] is '_id' and check_rem is True:
                y = y.values
                y = np.delete(y, 0, 1)
            else:
                y = y.values
        imp = Imputer(missing_values='NaN', strategy='median', axis=0)
        imp.fit(x)
        x = imp.transform(x)
        if y is not None:
            return x, y
        else:
            return x

