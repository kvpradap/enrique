import logging
import magellan as mg

from magellan.matcher.rulematcher import RuleMatcher
from collections import OrderedDict

class BooleanRuleMatcher(RuleMatcher):
    def __init__(self):
        self.name = 'BooleanRuleMatcher'
        self.rules = OrderedDict()
        self.rule_source = OrderedDict()
        self.rule_conjunct_list = OrderedDict()
        self.rule_cnt = 0

    def fit(self):
        pass

    def predict_candset(self, table):
        ltable = table.get_property('ltable')
        rtable = table.get_property('rtable')
        assert ltable is not None, 'Left table is not set'
        assert rtable is not None, 'Right table is not set'
        l_key = 'ltable.' + ltable.get_key()
        r_key = 'rtable.' + rtable.get_key()
        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)
        # keep track of valid ids
        y = []
        # iterate candidate set and process each row
        for idx, row in table.iterrows():
            # get the value of block attribute from ltuple
            l_row = l_tbl.ix[row[l_key]]
            r_row = r_tbl.ix[row[r_key]]
            res = self.apply_rules(l_row, r_row)
            if res is True:
                y.append(1)
            else:
                y.append(0)
        return y

    def predict(self, table=None, target_attr=None, append=False):
        if table  is not None:
            y = self.predict_candset(table)
            if target_attr is not None and append is True:
                table[target_attr] = y
                return table
            else:
                return y
        else:
            raise SyntaxError('The arguments supplied does not match the signatures supported !!!')



    def create_rule(self, conjunct_list, feature_table, name=None):
        if feature_table is None:
            logging.getLogger(__name__).error('Feature table is not given')
            return False
        # set the name
        if name is None:
            name = '_rule_' + str(self.rule_cnt)
            self.rule_cnt += 1

        fn_str = self.get_function_str(name, conjunct_list)

        if feature_table is not None:
            feat_dict = dict(zip(feature_table['feature_name'], feature_table['function']))
        else:
            feat_dict = dict(zip(self.feature_table['feature_name'], self.feature_table['function']))

        exec fn_str in feat_dict
        return feat_dict[name], name, fn_str

    def add_rule(self, conjunct_list, feature_table):
        if not isinstance(conjunct_list, list):
            conjunct_list = [conjunct_list]

        fn, name, fn_str = self.create_rule(conjunct_list, feature_table)

        self.rules[name] = fn
        self.rule_source[name] = fn_str
        self.rule_conjunct_list[name] = conjunct_list

        return True

    def del_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
            return False

        del self.rules[rule_name]
        del self.rule_source[rule_name]
        del self.rule_conjunct_list[rule_name]

        return True

    def view_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
        print(self.rule_source[rule_name])

    def get_rule_names(self):
        return self.rules.keys()

    def get_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
        return self.rules[rule_name]

    def apply_rules(self, ltuple, rtuple):
        for fn in self.rules.values():
            res = fn(ltuple, rtuple)
            if res is True:
                return True
        return False

    def get_function_str(self, name, conjunct_list):
        # create function str
        fn_str = "def " + name + "(ltuple, rtuple):\n"
        # add 4 tabs
        fn_str += '    '
        fn_str += 'return ' + ' and '.join(conjunct_list)
        return fn_str
