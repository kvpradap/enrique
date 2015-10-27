from collections import OrderedDict
import logging
class MatchTrigger(object):
    """
    Class to patch output from Matchers.
    Note:
    This class is similar to BooleanRuleMatcher except that this class switches predictions.
    """
    def __init__(self):
        self.cond_status = False
        self.rules = OrderedDict()
        self.rule_source = OrderedDict()
        self.rule_conjunct_list = OrderedDict()
        self.rule_cnt = 0
        self.value_to_set = 0


    def add_cond_rule(self, conjunct_list, feature_table):
        """
        Add rule to match trigger

        Parameters
        ----------
        conjunct_list : List of strings.
         List of predicates as in ['title_title_lev(ltuple, rtuple) > 0.8', 'name_name_mel(ltuple, rtuple)' > 0.6]

        feature_table : Pandas dataframe.
          Feature table containing information about features.
          see also:  get_features_for_blocking, get_features_from_matching, get_features

        Returns
        -------
        status : boolean, return True if the command was executed successfully.


        """
        if not isinstance(conjunct_list, list):
            conjunct_list = [conjunct_list]

        fn, name, fn_str = self.create_rule(conjunct_list, feature_table)

        self.rules[name] = fn
        self.rule_source[name] = fn_str
        self.rule_conjunct_list[name] = conjunct_list

        return True



    def add_cond_status(self, status):
        """
        Add boolean status that the condition is expected to satisfy

        Parameters
        ----------
        status : boolean, status that the user wants the condition to satisfy

        Returns
        -------
        ret_status : boolean, returns True if the command was executed successfully.
        """
        if not isinstance(status, bool):
            raise AssertionError('status is expected to be a boolean i.e True/False')
        self.cond_status = status
        return True

    def add_action(self, value):
        """
        Add action if the condition evaluates to condition status (see add_cond_rule, add_cond_status)

        Parameters
        ----------
        value : int (0/1). Value to be set if the condition evaluates to condition status

        Returns
        -------
        status : boolean, returns True if the command was executed successfully.

        """
        if value != 0 and value != 1:
            raise AssertionError('Currently magellan supports only values 0/1 as label value')
        self.value_to_set = value
        return True
    # --------------------- currently working on --------------------------
    def execute(self, input_table, label_column, inplace=True):
        ltable = input_table.get_property('ltable')
        rtable = input_table.get_property('rtable')
        assert ltable is not None, 'Left table is not set'
        assert rtable is not None, 'Right table is not set'
        assert label_column in input_table.columns, 'Label column not in the input table'
        if inplace == False:
            table = input_table.copy()
        else:
            table = input_table



        l_key = input_table.get_property('foreign_key_ltable')
        r_key = input_table.get_property('foreign_key_rtable')

        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)

        # keep track of valid ids
        y = []


        # iterate candidate set and process each row

        # l_dict = {}
        # header = list(l_df.columns)
        # key_idx = header.index(ltable.get_key())
        # for row in l_df.itertuples(index=False):
        #     k = row[key_idx]
        #     r = OrderedDict(zip(header, row))
        #     l_dict[k] = r
        #
        # r_dict = {}
        # header = list(r_df.columns)
        # key_idx = header.index(rtable.get_key())
        # for row in r_df.itertuples(index=False):
        #     k = row[key_idx]
        #     r = OrderedDict(zip(header, row))
        #     r_dict[k] = r

        # l_dict = {}
        # r_dict = {}
        # for k, r in l_df.iterrows():
        #     l_dict[k] = r
        # for k, r in r_df.iterrows():
        #     r_dict[k] = r


        column_names = list(input_table.columns)
        lid_idx = column_names.index(l_key)
        rid_idx = column_names.index(r_key)
        id_idx = column_names.index(input_table.get_key())

        label_idx = column_names.index(label_column)
        test_idx = 0
        idx = 0
        for row in input_table.itertuples(index=False):

            if row[label_idx] != self.value_to_set:
                # get the value of block attribute from ltuple
                # t.ix[t.index.values[0], feature_names]
                l_row = l_tbl.ix[row[lid_idx]]
                # l_row = l_tbl.ix[row.ix[row.index.values[0], l_key]]
                # r_row = r_tbl.ix[row.ix[row.index.values[0], r_key]]
                r_row = r_tbl.ix[row[rid_idx]]
                # l_row = l_dict[row[l_key]]
                # r_row = r_dict[row[r_key]]
                res = self.apply_rules(l_row, r_row)
                if test_idx == 0:
                    print l_row
                    print r_row
                    print res
                    print 'before : ' + str(table.iat[idx, label_idx])
                if res == self.cond_status:
                    # switch labels.
                    table.iat[idx, label_idx] = self.value_to_set
                if test_idx == 0:
                    print 'after : ' + str(table.iat[idx, label_idx])
                    test_idx = 1
            idx += 1
        return table


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
            if res == True:
                return True
        return False

    def get_function_str(self, name, conjunct_list):
        # create function str
        fn_str = "def " + name + "(ltuple, rtuple):\n"
        # add 4 tabs
        fn_str += '    '
        fn_str += 'return ' + ' and '.join(conjunct_list)
        return fn_str
