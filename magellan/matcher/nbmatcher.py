from magellan.matcher.mlmatcher import MLMatcher

from sklearn.naive_bayes import GaussianNB

class NBMatcher(MLMatcher):
    """
    Naive bayes matcher.
    """
    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name')
        if name is None:
            self.name = 'NaiveBayes'
        else:
            self.name = name
        super(NBMatcher, self).__init__()
        self.clf = GaussianNB(*args, **kwargs)


