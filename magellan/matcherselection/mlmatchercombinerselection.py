# imports
import numpy as np
import itertools

from magellan.matcherselection.mlmatcherselection__ import select_matcher
from magellan.matcher.ensemblematcher import EnsembleMatcher

def selector_matcher_combiner(matchers, combiners, x=None, y=None, table=None, exclude_attrs=None, target_attr=None,
                              weights=None, threshold=None, k=5):
    """
    Select best ensemble of matchers using cross validation

    Parameters
    ----------
    matchers : list of matcher objects
    combiners : list
        list of combiners to be used for ensemble,
        currently the following combiners are supported: "weighted", "majority"
    x : MTable, defaults to None
        of feature vectors
    y : MTable, defaults to None
        of labels
    table : MTable, defaults to None
            of feature vectors and user included attributes
    exclude_attrs: list,
            list of attributes to be excluded in 'table'
    target_attr : string,
            target attribute name containing labels
    weights : list of floats
        applies only when combiners contain "weighted".
        Weights to be applied to the perdicted results to combine
    threshold : float
        applies only when combiners contain "weighted".
        threshold value to be compared to get final prediction.
    k : integer,
        number of folds to be used for crossvalidation
    """
    if not isinstance(matchers, list):
        matchers = [matchers]
    if not isinstance(combiners, list):
        combiners = [combiners]
    matcher_list = get_matcher_list(matchers, combiners, weights, threshold)
    return select_matcher(matcher_list, x=x,  y=y, table=table, exclude_attrs=exclude_attrs, target_attr=target_attr, k=k)



def get_matcher_list(matchers, combiners, weights, threshold):
    ensemble_len = range(2, len(matchers) + 1)
    matcher_list = []
    matcher_list.extend(matchers)
    for l in ensemble_len:
        iter_combns = itertools.combinations(xrange(0, len(matchers)), l)
        for ic in iter_combns:
            for c in combiners:
                m = [matchers[i] for i in ic]
#                n = [matchers[i].get_name() for i in ic]
#                name = ','.join(n)
                if c is 'Weighted':
                    em = EnsembleMatcher(m, voting=c, weights=weights, threshold=threshold)
                else:
                    em = EnsembleMatcher(m, voting=c)
                matcher_list.append(em)
    return matcher_list



