import logging

from collections import OrderedDict
from magellan.blocker.blocker import Blocker
from magellan import MTable

class RuleBasedBlocker(Blocker):

    def __init__(self, *args, **kwargs):
        feature_table = kwargs.get('feature_table', None)
        if 'feature_table' in kwargs.keys():
            del kwargs['feature_table']
        self.feature_table = feature_table
        self.rules = OrderedDict()

        # meta data : should be removed if they are not useful.
        self.rule_source = OrderedDict()
        self.rule_cnt = 0

        super(Blocker, self).__init__(*args, **kwargs)

    def create_rule(self, conjunct_list, feature_table=None):
        if feature_table is None and self.feature_table is None:
            logging.getLogger(__name__).error('Either feature table is given as a parameter or use set_feature_table to '
                                          'set feature table')
            return False
        # set the name
        name = '_rule_'+ str(self.rule_cnt)
        self.rule_cnt += 1
        # create function str
        fn_str = "def " + name + "(ltuple, rtuple):\n"
        # add 4 tabs
        fn_str += '    '
        fn_str += 'return ' + ' and '.join(conjunct_list)

        if feature_table is not None:
            feat_dict = dict(zip(feature_table['feature_name'], feature_table['function']))
        else:
            feat_dict = dict(zip(self.feature_table['feature_name'], self.feature_table['function']))

        exec fn_str in feat_dict

        return feat_dict[name], name, fn_str

    def add_rule(self, conjunct_list, feature_table=None):
        if not isinstance(conjunct_list, list):
            conjunct_list = [conjunct_list]

        fn, name, fn_str = self.create_rule(conjunct_list, feature_table)

        self.rules[name] = fn
        self.rule_source[name] = fn_str

        return True

    def delete_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
            return False

        del self.rules[rule_name]
        del self.rule_source[rule_name]
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

    def set_feature_table(self, feature_table):
        if self.feature_table is not None:
            logging.getLogger(__name__).warning('Feature table is already set, changing it now will not recompile '
                                                'existing rules')
        self.feature_table = feature_table
        return True


    def block_tables(self, ltable, rtable, l_output_attrs=None, r_output_attrs=None):
        # do integrity checks
        l_output_attrs, r_output_attrs = self.check_attrs(ltable, rtable, l_output_attrs, r_output_attrs)
        block_list = []
        for i, l in ltable.iterrows():
            for j, r in rtable.iterrows():
                # check whether it passes
                res = self.apply_rules(l, r)
                if res is True:
                    d = OrderedDict()
                    # add left id first
                    ltable_id = 'ltable.' + ltable.get_key()
                    d[ltable_id] = l_out[ltable.get_key()]

                    # add right id
                    rtable_id = 'rtable.' + rtable.get_key()
                    d[rtable_id] = r_out[rtable.get_key()]

                    # add left attributes
                    if l_output_attrs:
                        l_out = l[l_output_attrs]
                        l_out.index = 'ltable.'+l_out.index
                        d.update(l_out.to_dict())

                    # add right attributes
                    if r_output_attrs:
                        r_out = r[r_output_attrs]
                        r_out.index = 'rtable.'+r_out.index
                        d.update(r_out.to_dict())
                    block_list.append(d)
        candset = MTable(block_list)
        # set metadata
        candset.set_property('ltable', ltable)
        candset.set_property('rtable', rtable)
        candset.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
        candset.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())
        return candset


    def block_candset(self, vtable):
        ltable = vtable.get_property('ltable')
        rtable = vtable.get_property('rtable')

        self.check_attrs(ltable, rtable, None, None)
        l_key = 'ltable.' + ltable.get_key()
        r_key = 'rtable.' + rtable.get_key()

        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)
        # keep track of valid ids
        valid = []
        # iterate candidate set and process each row
        for idx, row in vtable.iterrows():
            # get the value of block attribute from ltuple
            l_row = l_tbl.ix[row[l_key]]
            r_row = r_tbl.ix[row[r_key]]
            res = self.apply_rules(l_row, r_row)
            if res is True:
                valid.append(True)
            else:
                valid.append(False)
        out_table = vtable[valid]
        return out_table

    def block_tuples(self, ltuple, rtuple):
        return not self.apply_rules(ltuple, rtuple)


    # helper functions
    def check_attrs(self, ltable, rtable, l_output_attrs, r_output_attrs):
        # check keys are set
        assert ltable.get_key() is not None, 'Key is not set for left table'
        assert rtable.get_key() is not None, 'Key is not set for right table'
        # check output columns form a part of left, right tables
        if l_output_attrs:
            if not isinstance(l_output_attrs, list):
                l_output_attrs = [l_output_attrs]
            assert set(l_output_attrs).issubset(ltable.columns) is True, 'Left output attributes ' \
                                                                         'are not in left table'
            l_output_attrs = [x for x in l_output_attrs if x not in [ltable.get_key()]]

        if r_output_attrs:
            if not isinstance(r_output_attrs, list):
                r_output_attrs = [r_output_attrs]
            assert set(r_output_attrs).issubset(rtable.columns) is True, 'Right output attributes ' \
                                                                         'are not in right table'
            r_output_attrs = [x for x in r_output_attrs if x not in [rtable.get_key()]]

        return l_output_attrs, r_output_attrs




    def apply_rules(self, ltuple, rtuple):
        for fn in self.rules.values():
            res = fn(ltuple, rtuple)
            if res is True:
                return True
        return False


