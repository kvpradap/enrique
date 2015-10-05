from magellan.matcher.mlmatcher import MLMatcher

from sklearn.tree import DecisionTreeClassifier

class DTMatcher(MLMatcher):
    """
    Decision tree matcher
    """
    def __init__(self, *args, **kwargs):
        super(DTMatcher, self).__init__()

        name = kwargs.pop('name')
        if name is None:
            self.name = 'DecisionTree'
        else:
            self.name = name
        self.clf = DecisionTreeClassifier(*args, **kwargs)

