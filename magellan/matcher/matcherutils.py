from collections import OrderedDict
import sklearn.cross_validation as cv
import numpy as np

from magellan import MTable
import time

def train_test_split(labeled_data, test_size, train_size, random_state=80):
    idx_values = np.array(labeled_data.index.values)
    idx_train, idx_test = cv.train_test_split(idx_values, test_size=test_size, train_size=train_size,
                                              random_state=random_state)
    # create a MTable for train and test data
    lbl_train = MTable(labeled_data.ix[idx_train], key=labeled_data.get_key())
    lbl_test = MTable(labeled_data.ix[idx_test], key=labeled_data.get_key())

    # propogate properties
    lbl_train.set_property('key', labeled_data.get_key())
    lbl_train.set_property('ltable', labeled_data.get_property('ltable'))
    lbl_train.set_property('rtable', labeled_data.get_property('rtable'))
    lbl_train.set_property('foreign_key_ltable', labeled_data.get_property('foreign_key_ltable'))
    lbl_train.set_property('foreign_key_rtable', labeled_data.get_property('foreign_key_rtable'))

    lbl_test.set_property('key', labeled_data.get_key())
    lbl_test.set_property('ltable', labeled_data.get_property('ltable'))
    lbl_test.set_property('rtable', labeled_data.get_property('rtable'))
    lbl_test.set_property('foreign_key_ltable', labeled_data.get_property('foreign_key_ltable'))
    lbl_test.set_property('foreign_key_rtable', labeled_data.get_property('foreign_key_rtable'))

    result = OrderedDict()
    result['train'] = lbl_train
    result['test'] = lbl_test

    return result

def get_ts():
    t = int(round(time.time()*1e10))
    return str(t)[::-1]



