from magellan.matcher.mlmatcher import MLMatcher

from sklearn.ensemble import RandomForestClassifier

class RFMatcher(MLMatcher):
    """
    Randomforest matcher
    """
    def __init__(self, *args, **kwargs):
        super(RFMatcher, self).__init__()
        self.clf = RandomForestClassifier(*args, **kwargs)
        self.name = 'RandomForest'
