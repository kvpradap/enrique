# input : clf, t1, t2, feat_table, features.
# output:
# Summary : Num Trees: 10; Mean Probability of False match = 1/10; Mean Probability of True match = 9/10 ;
#           Match status : T/F
# Tree 1
#   --
#   --
#   -- Probability for non-match : ; Prob. for match :
from magellan.matcher.rfmatcher import RFMatcher
from magellan.debug.decisiontree import debug_dt, get_prob
def debug_rf(rf, t1, t2, feat_table, fv_columns, exclude_attrs):
    i = 1
    if isinstance(rf, RFMatcher):
        clf = rf.clf
    else:
        clf = rf

    if exclude_attrs is None:
        feature_names = fv_columns
    else:
        cols = [c not in exclude_attrs for c in fv_columns]
        feature_names = fv_columns[cols]

    prob = get_prob(clf, t1, t2, feat_table, feature_names)
    print "Summary: Num trees = " + len(clf.estimators_) + "; Mean Prob. of False match = " + prob[0] + \
                                                "; Mean Prob of True match = " + prob[1]
    print ""
    for e in clf.estimators_:
        print "Tree " + str(i)
        i += 1
        p = debug_dt(e, t1, t2, feat_table, feature_names, exclude_attrs, ensemble_flag=True)
        print "-----"





