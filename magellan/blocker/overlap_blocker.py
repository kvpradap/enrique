
from magellan.blocker.blocker import Blocker
import pyximport; pyximport.install()
import logging
import magellan as mg
import math

from magellan.cython.test_functions import ngrams
from magellan.utils.helperfunctions import remove_non_ascii
from magellan import MTable
from collections import Counter, OrderedDict

import re, string
import pandas as pd

logger = logging.getLogger(__name__)

class OverlapBlocker(Blocker):

    def __init__(self):
        self.stop_words = ['a', 'an', 'and', 'are', 'as', 'at',
              'be', 'by', 'for', 'from',
              'has', 'he', 'in', 'is', 'it',
              'its', 'on', 'that', 'the', 'to',
              'was', 'were', 'will', 'with']
        self.regex_punctuation = re.compile('[%s]'
                                % re.escape(string.punctuation))
        super(OverlapBlocker, self).__init__()



    def block_tables(self, ltable, rtable,
                     l_overlap_attr, r_overlap_attr,
                     rem_stop_words = False,
                     qgram=None, word_level=True, overlap_size=1,
                     l_output_attrs=None, r_output_attrs=None

                     ):
        """
        Block tables with overlap blocker

        Parameters
        ----------
        ltable, rtable : MTables, input MTables to block
        l_overlap_attr, r_overlap_attr : String, overlap attribute from left and right table
        rem_stop_words : flag to indicate whether stop words should be removed
        qgram : int, value of q in qgram tokenizer. Default value is None
        word_level : boolean, flag to indicate to use word level tokenizer
        overlap_size : int, number of tokens to overlap
        l_output_attrs, r_output_attrs - list of attribtues to be included in the output table

        Returns
        -------
        result : MTable
        """
        # do some integrity checks
        if l_overlap_attr not in ltable.columns:
            raise AssertionError('Left overlap attribute  not in ltable columns')
        if r_overlap_attr not in rtable.columns:
            raise AssertionError('Right overlap attribute not in rtable columns')

        l_output_attrs, r_output_attrs = self.check_attrs(ltable, rtable, l_output_attrs, r_output_attrs)

        if word_level == True and qgram != None:
            raise SyntaxError('Parameters word_level and qgram cannot be set together; Note that world_level is set'
                              'to true by default, so explicity set word_level=False to use qgram')



        # remove nans
        l_df = self.rem_nan(ltable, l_overlap_attr)
        r_df = self.rem_nan(rtable, r_overlap_attr)

        l_df.reset_index(inplace=True, drop=True)
        r_df.reset_index(inplace=True, drop=True)

        l_df['_dummy_'] = 1
        r_df['_dummy_'] = 1

        if l_df.dtypes[l_overlap_attr] != object:
            logger.warning('Left overlap attribute is not of type string; converting to string temporarily')
            l_df[l_overlap_attr] = l_df[l_overlap_attr].astype(str)

        if r_df.dtypes[r_overlap_attr] != object:
            logger.warning('Right overlap attribute is not of type string; converting to string temporarily')
            r_df[r_overlap_attr] = r_df[r_overlap_attr].astype(str)



        l_dict = {}
        r_dict = {}
        for k, r in l_df.iterrows():
            l_dict[k] = r
        for k, r in r_df.iterrows():
            r_dict[k] = r

        l_col_values_chopped = self.process_table(l_df, l_overlap_attr, qgram, rem_stop_words)# zip token list with index-val
        zipped_l_col_values = zip(l_col_values_chopped, range(0, len(l_col_values_chopped)))
        appended_l_col_idx_values = [self.append_index_values(v[0], v[1]) for v in zipped_l_col_values]
        inv_idx = {}
        if mg._verbose:
            print 'Creating inverted index '
        sink = [self.compute_inv_index(t, inv_idx) for c in appended_l_col_idx_values for t in c]
        if mg._verbose:
            print 'Done'

        r_col_values_chopped = self.process_table(r_df, r_overlap_attr, qgram, rem_stop_words)
        r_idx = 0;
        l_key =  ltable.get_key()
        r_key = rtable.get_key()
        block_list = [] # misnomer - should be white list
        if mg._verbose:
            count = 0
            per_count = math.ceil(mg._percent/100.0*len(rtable))
            print per_count

        df_list = []
        for col_values in r_col_values_chopped:
            if mg._verbose:
                count += 1
                if count%per_count == 0:
                    print str(mg._percent*count/per_count) + ' percentage done !!!'

            qualifying_ltable_indices = self.get_potential_match_indices(col_values, inv_idx, overlap_size)
            r_row = r_dict[r_idx]
            r_row_dict = r_row.to_frame().T
            #r_row_dict['dummy'] = 1
            l_rows_dict = l_df.iloc[qualifying_ltable_indices]
            #l_rows_dict['dummy'] = 1
            df = l_rows_dict.merge(r_row_dict, on='_dummy_', suffixes=('_ltable', '_rtable'))
            df_list.append(df)
            r_idx += 1

        candset = pd.concat(df_list)
    # get output columns
        retain_cols, final_cols = self.output_columns(ltable.get_key(), rtable.get_key(), list(candset.columns),
                                                   l_output_attrs, r_output_attrs)


        candset = candset[retain_cols]
        candset.columns = final_cols
        if len(candset) > 0:
            candset.sort(['ltable.'+ltable.get_key(), 'rtable.'+rtable.get_key()], inplace=True)
            candset.reset_index(inplace=True, drop=True)
        candset = MTable(candset)


        # set metadata
        candset.set_property('ltable', ltable)
        candset.set_property('rtable', rtable)
        candset.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
        candset.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())
        return candset


    def block_candset(self,vtable, l_overlap_attr, r_overlap_attr, rem_stop_words=False,
                     qgram=None, word_level=True, overlap_size=1):

        """
        Block candidateset with overlap blocker

        Parameters
        ----------
        vtable : MTable, candidate set to block
        l_overlap_attr, r_overlap_attr : String, overlap attribute from left and right table
        rem_stop_words : flag to indicate whether stop words should be removed
        qgram : int, value of q in qgram tokenizer. Default value is None
        word_level : boolean, flag to indicate to use word level tokenizer
        overlap_size : int, number of tokens to overlap
        l_output_attrs, r_output_attrs - list of attribtues to be included in the output table

        Returns
        -------
        result : MTable
        """


        ltable = vtable.get_property('ltable')
        rtable = vtable.get_property('rtable')


        self.check_attrs(ltable, rtable, None, None)
        # do some integrity checks
        if l_overlap_attr not in ltable.columns:
            raise AssertionError('Left overlap attribute  not in ltable columns')
        if r_overlap_attr not in rtable.columns:
            raise AssertionError('Right overlap attribute not in rtable columns')

        l_key = vtable.get_property('foreign_key_ltable')
        r_key = vtable.get_property('foreign_key_rtable')

        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)

        # create look up table for quick access of rows
        l_dict = {}
        for k, r in l_tbl.iterrows():
            l_dict[k] = r
        r_dict = {}
        for k, r in r_tbl.iterrows():
            r_dict[k] = r

        valid = []

        column_names = list(vtable.columns)
        lid_idx = column_names.index(l_key)
        rid_idx = column_names.index(r_key)

        if mg._verbose:
            count = 0
            per_count = math.ceil(mg._percent/100.0*len(vtable))
            print per_count

        for row in vtable.itertuples(index=False):
            if mg._verbose:
                count += 1
                if count%per_count == 0:
                    print str(mg._percent*count/per_count) + ' percentage done !!!'

            l_row = l_dict[row[lid_idx]]
            r_row = r_dict[row[rid_idx]]

            num_overlap = self.get_token_overlap_bt_two_tuples(l_row, r_row,
                                                               l_overlap_attr, r_overlap_attr,
                                                               qgram, rem_stop_words)

            if num_overlap >= overlap_size:
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


    def block_tuples(self, ltuple, rtuple, l_overlap_attr, r_overlap_attr,rem_stop_words = False,
                     qgram=None, word_level=True, overlap_size=1):
        """
        Block tables with overlap blocker

        Parameters
        ----------
        ltuple, rtuple : Pandas series, tuples to block
        l_overlap_attr, r_overlap_attr : String, overlap attribute from left and right table
        rem_stop_words : flag to indicate whether stop words should be removed
        qgram : int, value of q in qgram tokenizer. Default value is None
        word_level : boolean, flag to indicate to use word level tokenizer
        overlap_size : int, number of tokens to overlap
        l_output_attrs, r_output_attrs - list of attribtues to be included in the output table

        Returns
        -------
        result : boolean, True if the tuple pair is dropped.


        """

        num_overlap = self.get_token_overlap_bt_two_tuples(ltuple, rtuple,
                                                               l_overlap_attr, r_overlap_attr,
                                                               qgram, rem_stop_words)
        if num_overlap < overlap_size:
            return True
        else:
            return False

    def get_token_overlap_bt_two_tuples(self, l_row, r_row,
                                        l_overlap_attr, r_overlap_attr,
                                        qgram, rem_stop_words):
        l_val = l_row[l_overlap_attr]
        r_val = r_row[r_overlap_attr]
        if l_val == None or r_val == None:
            return 0
        if not isinstance(l_val, basestring):
            l_val = str(l_val)
        if not isinstance(r_val, basestring):
            r_val = str

        l_val_ls = set(self.process_val(l_val, l_overlap_attr, qgram, rem_stop_words))
        r_val_ls = set(self.process_val(r_val, r_overlap_attr, qgram, rem_stop_words))

        return len(l_val_ls.intersection(r_val_ls))




    def get_row_dict_with_output_attrs(self, l, r, l_key, r_key, l_output_attrs, r_output_attrs):
        d = OrderedDict()
        ltable_id = 'ltable.' + l_key
        d[ltable_id] = l[l_key]

        # add right id
        rtable_id = 'rtable.' + r_key
        d[rtable_id] = r[r_key]

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
        return d

    def process_val(self, val, overlap_attr, qgram, rem_stop_words):
        val = remove_non_ascii(val)
        val = self.rem_punctuations(val).lower()
        chopped_vals = val.split()
        if rem_stop_words == True:
            chopped_vals = self.rem_stopwords(chopped_vals)
        if qgram != None:
            values = ' '.join(chopped_vals)
            chopped_vals = ngrams(values, qgram)
        return chopped_vals





    def process_table(self, df, overlap_attr, qgram, rem_stop_words):
        # get ltable attr column
        attr_col_values = df[overlap_attr].values
        # remove non-ascii chars
        attr_col_values = [remove_non_ascii(v) for v in attr_col_values]

        # remove special characters
        attr_col_values = [self.rem_punctuations(v).lower() for v in attr_col_values]
        # chop the attribute values
        col_values_chopped = [v.split() for v in attr_col_values]
        # remove stop words
        if rem_stop_words == True:
            col_values_chopped = [self.rem_stopwords(v) for v in col_values_chopped]
        if qgram is not None:
            values = [' '.join(v) for v in col_values_chopped]
            col_values_chopped = [ngrams(v, qgram) for v in values]

        return col_values_chopped

    def rem_punctuations(self, s):
        return self.regex_punctuation.sub('', s)

    def rem_stopwords(self, ls):
        return [t for t in ls if t not in self.stop_words]

    def append_index_values(self, ls, idx):
        ls = set(ls)
        return [(v, idx) for v in ls]

    def compute_inv_index(self, tok_idx, idx):
        #print '.',
        ls = idx.pop(tok_idx[0], None)
        if ls is None:
            ls = list()
            ls.append(tok_idx[1])
            idx[tok_idx[0]] = ls
        else:
            ls.append(tok_idx[1])
            idx[tok_idx[0]] = ls

    def probe_inv_index_for_a_token(self, token, inverted_index):
         return inverted_index.get(token, None)

    def probe_inv_index(self, ls, inverted_index):
        return [self.probe_inv_index_for_a_token(t, inverted_index) for t in ls]

    def get_freq_count(self, ls):
        p = list()
        dummy = [p.extend(k) for k in ls if k is not None]
        d = dict(Counter(p))
        return d

    def get_qualifying_indices(self, freq_dict, overlap_size):
        q_indices = []
        for k, v in freq_dict.iteritems():
            if v >= overlap_size:
                q_indices.append(k)
        return q_indices

    def get_potential_match_indices(self, ls, inverted_index, overlap_size):
        indices = self.probe_inv_index(ls, inverted_index)
        freq_dict = self.get_freq_count(indices)
        qualifying_indices = self.get_qualifying_indices(freq_dict, overlap_size)
        return qualifying_indices


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





