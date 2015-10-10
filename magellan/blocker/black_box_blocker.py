import logging

import pandas as pd
from magellan.blocker.blocker import Blocker
from magellan import MTable
from collections import OrderedDict



class BlackBoxBlocker(Blocker):
    def __init__(self, *args, **kwargs):
        super(Blocker, self).__init__(*args, **kwargs)
        self.black_box_function = None

    def set_black_box_function(self, function):
        self.black_box_function = function
        return True

    def block_tables(self, ltable, rtable, l_output_attrs=None,
                     r_output_attrs=None, verbose=False, percent=10):
        l_output_attrs, r_output_attrs = self.check_attrs(ltable, rtable, l_output_attrs, r_output_attrs)
        block_list = []
        if verbose:
            count = 0
            per_count = percent/100.0*len(ltable)*len(rtable)

        for i, l in ltable.iterrows():
            for j, r in rtable.iterrows():
                if verbose:
                    count += 1
                    if count%per_count == 0:
                        print str(percent*count/per_count) + ' percentage done !!!'

                res = self.black_box_function(l, r)
                if not res is True:
                    d = OrderedDict()
                   # add left id first
                    ltable_id = 'ltable.' + ltable.get_key()
                    d[ltable_id] = l[ltable.get_key()]

                    # add right id
                    rtable_id = 'rtable.' + rtable.get_key()
                    d[rtable_id] = r[rtable.get_key()]

                    # add left attributes
                    if l_output_attrs:
                        l_out = l[l_output_attrs]
                        l_out.index = 'ltable.'+l_out.index
                        d.update(l_out)

                    # add right attributes
                    if r_output_attrs:
                        r_out = r[r_output_attrs]
                        r_out.index = 'rtable.'+r_out.index
                        d.update(r_out)
                    block_list.append(d)
        candset = pd.DataFrame(block_list)
        ret_cols = self.get_attrs_to_retain(ltable.get_key(), rtable.get_key(), l_output_attrs, r_output_attrs)
        if len(candset) > 0:
            candset = MTable(candset[ret_cols])
        else:
            candset = MTable(candset, columns=ret_cols)

        # set metadata
        candset.set_property('ltable', ltable)
        candset.set_property('rtable', rtable)
        candset.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
        candset.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())
        return candset


    def block_candset(self, vtable, verbose=False, percent=10):
        ltable = vtable.get_property('ltable')
        rtable = vtable.get_property('rtable')
        self.check_attrs(ltable, rtable, None, None)
        l_key = vtable.get_property('foreign_key_ltable')
        r_key = vtable.get_property('foreign_key_rtable')

        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)

        #keep track of valid ids

        valid = []
        #iterate candidate set and process each row
        if verbose:
            count = 0
            per_count = percent/100.0*len(ltable)*len(rtable)

        for idx, row in vtable.iterrows():
            if verbose:
                count += 1
                if count%per_count == 0:
                    print str(percent*count/per_count) + ' percentage done !!!'

            l_row = l_tbl.ix[row[l_key]]
            r_row = r_tbl.ix[row[r_key]]
            res = self.black_box_function(l_row, r_row)
            if not res is True:
                valid.append(True)
            else:
                valid.append(False)

        if len(vtable) > 0:
            out_table = MTable(vtable[valid], key=vtable.get_key())
        else:
            out_table = MTable(columns=vtable.columns, key=vtable.get_key())

        out_table.set_property('ltable', ltable)
        out_table.set_property('rtable', rtable)
        out_table.set_property('foreign_key_ltable', vtable.get_property('foreign_key_ltable'))
        out_table.set_property('foreign_key_rtable', vtable.get_property('foreign_key_rtable'))
        return out_table


    def block_tuples(self, ltuple, rtuple):
        if self.black_box_function is None:
            raise AssertionError('Black box function is not set')
        return self.black_box_function(ltuple, rtuple)



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

    def get_attrs_to_retain(self, l_id, r_id, l_col, r_col):
        ret_cols=[]
        ret_cols.append('ltable.' + l_id)
        ret_cols.append('rtable.' + r_id)
        if l_col:
            ret_cols.extend(['ltable.'+c for c in l_col])
        if r_col:
            ret_cols.extend(['rtable.'+c for c in r_col])
        return ret_cols