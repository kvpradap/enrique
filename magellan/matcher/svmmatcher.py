from magellan.matcher.mlmatcher import MLMatcher
from sklearn.svm import SVC
class SVMMatcher(MLMatcher):
    """
    SVM matcher
    """
    def __init__(self, *args, **kwargs):
        super(SVMMatcher, self).__init__(*args, **kwargs)
        self.clf = SVC(*args, **kwargs)
        self.name = 'SVM'
