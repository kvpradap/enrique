from magellan.matcher.mlmatcher import MLMatcher
from sklearn.linear_model import LogisticRegression

class LogRegMatcher(MLMatcher):
    """
    Logistic regression matcher
    """
    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name')
        if name is None:
            self.name = 'LogisticRegression'
        else:
            self.name = name
        super(LogRegMatcher, self).__init__()
        self.clf = LogisticRegression(*args, **kwargs)
