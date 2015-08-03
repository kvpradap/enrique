import numpy as np
import pandas as pd

from magellan.blocker.blocker import Blocker


class AttrEquivBlocker(Blocker):
    def block_tables(self, ltable, rtable, l_block_attr, r_block_attr,
                     l_output_attrs=None, r_output_attrs=None):
        assert ltable is not None, 'ltable is None'
        assert rtable is not None, 'rtable is None'

        # check whether keys are set
        assert ltable.get_key() is not None, 'Key is not set in ltable'
        assert rtable.get_key() is not None, 'Key is not set in rtable'

        # check integrity of attrs


        return None

    def block_tuples(self, ltuple, rtuple):
        return None

    def block_candset(self, vtable, l_block_attr, r_block_attr):
        return None


# --------------------------------------------------------------------------------------
# helper functions
def prefix_names(name, prefix):
    return prefix + str(name)


def check_attrs(l_attrs, r_attrs, l_block_attr, r_block_attr, l_out_attrs, r_out_attrs):

    assert l_block_attr is not None, 'Left block attribute cannot be None'
    assert r_block_attr is not None, 'Right block attribute cannot be None'

    #assert set(l_block_attr).issubset(l_attrs)  is

    return None

def get_attrs(ltable, rtable, l_attr, r_attr, l_out_attrs, r_out_attrs):
    return None

