from magellan.matcher.mlmatcher import MLMatcher
from sklearn.linear_model import LinearRegression
from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.base import TransformerMixin

class LinRegClassifierSKLearn(BaseEstimator, ClassifierMixin, TransformerMixin):
    def __init__(self, *args, **kwargs):
        self.clf = LinearRegression(*args, **kwargs)
    def fit(self, X, y):
        y = (2 * y) - 1
        self.clf.fit(X, y)
        return self

    def predict(self, X):
        y = self.clf.predict(X)
        y = (2 * (y > 0)) - 1
        y[y == -1] = 0
        return y

    def get_params(self, deep=True):
        return self.clf.get_params(deep=deep)


class LinRegMatcher(MLMatcher):
    """
    Linear regression matcher
    """
    def __init__(self, *args, **kwargs):
        super(LinRegMatcher, self).__init__()
        name = kwargs.pop('name')
        if name is None:
            self.name = 'LinearRegression'
        else:
            self.name = name
        self.clf = LinRegClassifierSKLearn(*args, **kwargs)



