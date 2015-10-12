from magellan.blocker.blocker import Blocker
import pyximport; pyximport.install()

from magellan.cython.test_functions import *
from collections import Counter

import re, string

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
                     qgram=None, word_level=True, overlap_size=2,
                     rem_stop_words = True,
                     l_output_attrs=None, r_output_attrs=None
                     ):
        # remove nans
        l_df = self.rem_nan(ltable, l_overlap_attr)
        r_df = self.rem_nan(rtable, r_overlap_attr)

        l_df.reset_index(inplace=True, drop=True)
        r_df.reset_index(inplace=True, drop=True)

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
        sink = [self.compute_inv_index(t, inv_idx) for t in appended_l_col_idx_values]

        r_col_values_chopped = self.process_table(r_df, r_overlap_attr, qgram, rem_stop_words)












        pass

    def process_table(self, df, overlap_attr, qgram, rem_stop_words):
        # get ltable attr column
        attr_col_values = df[overlap_attr].values
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

    # def get_qualifying_indices(self, freq_dict, overlap_size):
        








