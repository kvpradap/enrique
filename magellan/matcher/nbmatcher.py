from magellan.matcher.mlmatcher import MLMatcher

from sklearn.naive_bayes import GaussianNB

class NBMatcher(MLMatcher):
    """
    Naive bayes matcher.
    """
    def __init__(self, *args, **kwargs):
        super(NBMatcher, self).__init__(*args, **kwargs)
        self.clf = GaussianNB(*args, **kwargs)
        self.name = 'NaiveBayes'

