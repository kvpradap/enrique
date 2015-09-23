from magellan.matcher.mlmatcher import MLMatcher
from sklearn.linear_model import LogisticRegression

class LogRegMatcher(LogisticRegression):
    """
    Naive bayes matcher.
    """
    def __init__(self, *args, **kwargs):
        super(LogRegMatcher, self).__init__(*args, **kwargs)
        self.clf = LogisticRegression(*args, **kwargs)
        self.name = 'LogisticRegression'
