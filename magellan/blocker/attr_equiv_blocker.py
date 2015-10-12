#imports
import pandas as pd
import numpy as np

from magellan.blocker.blocker import Blocker
from magellan.core.mtable import MTable
import magellan as mg

class AttrEquivalenceBlocker(Blocker):

    def block_tables(self, ltable, rtable, l_block_attr, r_block_attr,
                     l_output_attrs=None, r_output_attrs=None):
        """
        Block tables based on l_block_attr, r_block_attr equivalence (similar to equi-join)

        Parameters
        ----------
        ltable, rtable : MTable
            Input MTables
        l_block_attr, r_block_attr : string,
            attribute names in ltable, rtable
        l_output_attrs, r_output_attrs : list (of strings), defaults to None
            attribute names to be included in the output table

        Returns
        -------
        blocked_table : MTable
            Containing tuple pairs whose l_block_attr and r_block_attr values are same

        Notes
        -----
        Output MTable contains the following three attributes
            * _id
            * id column from ltable
            * id column from rtable

        Also, the properties of blocked table is updated with following key-value pairs
            * ltable - ref to ltable
            * rtable - ref to rtable
            * key
            * foreign_key_ltable - string, ltable's  id attribute name
            * foreign_key_rtable - string, rtable's id attribute name
        """

        # do integrity checks
        l_output_attrs, r_output_attrs = self.check_attrs(ltable, rtable, l_block_attr, r_block_attr,
                                                     l_output_attrs, r_output_attrs)
        # remove nans
        l_df = self.rem_nan(ltable, l_block_attr)
        r_df = self.rem_nan(rtable, r_block_attr)

        candset = pd.merge(l_df, r_df, left_on=l_block_attr, right_on=r_block_attr,
                           suffixes=('_ltable', '_rtable'))

        # get output columns
        retain_cols, final_cols = self.output_columns(ltable.get_key(), rtable.get_key(), list(candset.columns),
                                                   l_output_attrs, r_output_attrs)

        #print candset.columns
        #print retain_cols
        candset = candset[retain_cols]
        candset.columns = final_cols
        candset = MTable(candset)
        #key_name = candset._get_name_for_key(candset.columns)
        #candset.add_key(key_name)

        # set metadata
        candset.set_property('ltable', ltable)
        candset.set_property('rtable', rtable)
        candset.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
        candset.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())
        return candset


    # blocking over candidate set
    def block_candset(self, vtable, l_block_attr, r_block_attr):
        """
        Block candidate set (virtual MTable) based on l_block_attr, r_block_attr equivalence (similar to equi-join)

        Parameters
        ----------
        vtable : MTable
            Input candidate set
        l_block_attr, r_block_attr : string,
            attribute names in ltable, rtable

        Returns
        -------
        blocked_table : MTable
            Containing tuple pairs whose l_block_attr and r_block_attr values are same

        Notes
        -----
        Output MTable contains the following three attributes
            * _id
            * id column from ltable
            * id column from rtable

        Also, the properties of blocked table is updated with following key-value pairs
            * ltable - ref to ltable
            * rtable - ref to rtable
            * key
            * foreign_key_ltable - string, ltable's  id attribute name
            * foreign_key_rtable - string, rtable's id attribute name
        """
        # do integrity checks
        ltable = vtable.get_property('ltable')
        rtable = vtable.get_property('rtable')

        self.check_attrs(ltable, rtable, l_block_attr, r_block_attr, None, None)
        l_key = 'ltable.' + ltable.get_key()
        r_key = 'rtable.' + rtable.get_key()

        # convert to dataframes
        l_df = ltable.to_dataframe()
        r_df = rtable.to_dataframe()

        # set index for convenience
        l_df.set_index(ltable.get_key(), inplace=True)
        r_df.set_index(rtable.get_key(), inplace=True)

        # keep track of valid ids
        valid = []
        # iterate candidate set and process each row
        for idx, row in vtable.iterrows():
            # get the value of block attribute from ltuple
            l_val = l_df.ix[row[l_key], l_block_attr]
            r_val = r_df.ix[row[r_key], r_block_attr]
            if l_val != np.NaN and r_val != np.NaN:
                if l_val == r_val:
                    valid.append(True)
                else:
                    valid.append(False)
            else:
                valid.append(False)
        
        # should be modified
        if len(vtable) > 0:
            out_table = MTable(vtable[valid], key=vtable.get_key())
        else:
            out_table = MTable(columns=vtable.columns, key=vtable.get_key())
        out_table.set_property('ltable', ltable)
        out_table.set_property('rtable', rtable)
        out_table.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
        out_table.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())
        return out_table

    # blocking over tuples
    def block_tuples(self, ltuple, rtuple, l_block_attr, r_block_attr):
        """
        Block tuples based on l_block_attr and r_block_attr

        Parameters
        ----------
        ltuple, rtuple : pandas Series,
            Input tuples
        l_block_attr, r_block_attr : string,
            attribute names in ltuple and r_tuple

        Returns
        -------
        status : boolean,
         True is the tuple pair is blocked (i.e the values in l_block_attr and r_block_attr are different)
        """
        return ltuple[l_block_attr] != rtuple[r_block_attr]

    # check integrity of attrs in l_block_attr, r_block_attr
    def check_attrs(self, ltable, rtable, l_block_attr, r_block_attr, l_output_attrs, r_output_attrs):

        # check keys are set
        assert ltable.get_key() is not None, 'Key is not set for left table'
        assert rtable.get_key() is not None, 'Key is not set for right table'

        # check block attributes form a subset of left and right tables
        if not isinstance(l_block_attr, list):
            l_block_attr = [l_block_attr]
        assert set(l_block_attr).issubset(ltable.columns) is True, 'Left block attribute is not in left table'

        if not isinstance(r_block_attr, list):
            r_block_attr = [r_block_attr]
        assert set(r_block_attr).issubset(rtable.columns) is True, 'Right block attribute is not in right table'

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



    # get output columns
    def output_columns(self, l_key, r_key, col_names, l_output_attrs, r_output_attrs):

        ret_cols = []
        fin_cols = []

        # retain id columns from merge
        ret_l_id = [self.retain_names(x, col_names, '_ltable') for x in [l_key]]
        ret_r_id = [self.retain_names(x, col_names, '_rtable') for x in [r_key]]
        ret_cols.extend(ret_l_id)
        ret_cols.extend(ret_r_id)

        # retain output attrs from merge
        if l_output_attrs:
            ret_l_col = [self.retain_names(x, col_names, '_ltable') for x in l_output_attrs]
            ret_cols.extend(ret_l_col)
        if r_output_attrs:
            ret_r_col = [self.retain_names(x, col_names, '_rtable') for x in r_output_attrs]
            ret_cols.extend(ret_r_col)

        # final columns in the output
        fin_l_id = [self.final_names(x, 'ltable.') for x in [l_key]]
        fin_r_id = [self.final_names(x, 'rtable.') for x in [r_key]]
        fin_cols.extend(fin_l_id)
        fin_cols.extend(fin_r_id)

        # final output attrs from merge
        if l_output_attrs:
            fin_l_col = [self.final_names(x, 'ltable.') for x in l_output_attrs]
            fin_cols.extend(fin_l_col)
        if r_output_attrs:
            fin_r_col = [self.final_names(x, 'rtable.') for x in r_output_attrs]
            fin_cols.extend(fin_r_col)

        return ret_cols, fin_cols


    def retain_names(self, x, col_names, suffix):
        if x in col_names:
            return x
        else:
            return str(x) + suffix

    def final_names(self, x, prefix):
        return prefix + str(x)