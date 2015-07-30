import numpy as np
import pandas as pd

from magellan.blocker.blocker import Blocker


class AttrEquivBlocker(Blocker):
    def block_tables(self, ltable, rtable, l_block_attr, r_block_attr,
                     l_output_attrs=None, r_output_attrs=None):
        return None

    def block_tuples(self, ltuple, rtuple):
        return None

    def block_candset(self, vtable, l_block_attr, r_block_attr):
        return None


# --------------------------------------------------------------------------------------
# helper functions
def prefix_names(name, prefix):
    return prefix + str(name)


def check_attrs(ltable, rtable, l_attr, r_attr, l_out_attrs, r_out_attrs):
    # l_out_attrs, r_out_attrs should form a part of ltable and rtable respc.
    # l_attr, r_attr should form a part of ltable and rtable respc.
    # l_attr, r_attr must be a single attr and their types must be same


    return None

def get_attrs(ltable, rtable, l_attr, r_attr, l_out_attrs, r_out_attrs):
    return None

