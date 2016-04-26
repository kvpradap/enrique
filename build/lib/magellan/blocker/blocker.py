import numpy as np
import logging
logger = logging.getLogger(__name__)
class Blocker(object):
    pass
    # remove nows with nan values at block_attr
    def rem_nan(self, table, block_attr):
        l = table.index.values[np.where(table[block_attr].notnull())[0]]
        return table.ix[l]
