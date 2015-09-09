from collections import OrderedDict
from magellan.trigger import Trigger

import logging

class MatchNegativeRuleTrigger(Trigger):

    def __init__(self, *args, **kwargs):
        self.rules = OrderedDict()
        self.rule_source = OrderedDict()
        self.rule_cnt = 0
        super(Trigger, self).__init__(*args, **kwargs)

    def create_rule(self, conjunct_list, feature_table):
        if feature_table is None:
            logging.getLogger(__name__).error('Feature table is not given as input')
            return False



