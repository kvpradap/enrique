import pandas as pd

from magellan.core.mtable import MTable

def read_csv(*args, **kwargs):
    if kwargs.has_key('key') is False:
        raise AttributeError('Key is not specified')
    key = kwargs.pop('key', None)
    df = pd.read_csv(*args, **kwargs)
    if key is not None:
        return MTable(df, key=key)
    else:
        df = MTable(df)
        df.add_key('_m_id')
        return df

