import magellan as mg
from magellan.matcher.mlmatcher import MLMatcher

from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import Imputer


class NBMatcher(MLMatcher):
    """
    Naive bayes matcher.
    """

    def __init__(self, *args, **kwargs):
        super(NBMatcher, self).__init__(*args, **kwargs)
        self.clf = GaussianNB(*args, **kwargs)

    # -----------------------------------------------------------
    # fit routines
    def fit_sklearn(self, x, y):
        # get the data in a format that sklearn can operate on
        x, y = self.get_data_for_sklearn(x, y)
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
        y = table[target_attr]
        self.fit_sklearn(x, y)

    def fit(self, x=None, y=None, table=None, exclude_attrs=None, target_attr=None):
        if x is not None and y is not None:
            self.fit_sklearn(x, y)
        elif (table is not None and exclude_attrs is not None) and target_attr is not None:
            self.fit_ex_attrs(table, exclude_attrs, target_attr)
        else:
            raise SyntaxError('The arguments supplied does not match the signatures supported !!!')

    # -----------------------------------------------------------
    # predict routines

    # call predict method of sklearn classifier
    def predict_sklearn(self, x):
        x = self.get_data_for_sklearn(x)
        return self.clf.predict(x)

    # variant of predict method, where data is derived based on exclude attributes
    def predict_ex_attrs(self, table, exclude_attrs):
        if not isinstance(exclude_attrs, list):
            exclude_attrs = [exclude_attrs]
        table = table.to_dataframe()
        attrs_to_project = mg.diff(table.columns, exclude_attrs)
        x = table[attrs_to_project]
        y = self.predict_sklearn(x)
        # table[target_attr] = y
        return y

    # def predict_ex_sklearn_attrs(self, table, x):
    #     y = self.predict_sklearn(x)
    #     #table[target_attr] = y
    #     return y

    # predict method
    def predict(self, table=None, x=None, exclude_attrs=None, target_attr=None, append=False):
        if x is not None:
            y = self.predict_sklearn(x)
            if target_attr is not None and append is True:
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

    # -----------------------------------------------------------
    # common routines

    def get_data_for_sklearn(self, x, y=None):
        x = x.values
        if y is not None:
            y = y.values
        imp = Imputer(missing_values='NaN', strategy='median', axis=0)
        imp.fit(x)
        x = imp.transform(x)
        if y is not None:
            return x, y
        else:
            return x
