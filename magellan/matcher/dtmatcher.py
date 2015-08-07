from magellan.matcher.mlmatcher import MLMatcher

from sklearn.tree import DecisionTreeClassifier

class DTMatcher(MLMatcher):
    """
    Decision tree matcher
    """
    def __init__(self, *args, **kwargs):
        super(DTMatcher, self).__init__(*args, **kwargs)
        self.clf = DecisionTreeClassifier(*args, **kwargs)
