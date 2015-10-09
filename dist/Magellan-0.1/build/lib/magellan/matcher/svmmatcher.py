from magellan.matcher.mlmatcher import MLMatcher
from sklearn.svm import SVC
class SVMMatcher(MLMatcher):
    """
    SVM matcher
    """
    def __init__(self, *args, **kwargs):
        super(SVMMatcher, self).__init__()
        name = kwargs.pop('name')
        if name is None:
            self.name = 'SVM'
        else:
            self.name = name
        self.clf = SVC(*args, **kwargs)
