import logging
import magellan as mg
from magellan.core.mtable import MTable
def label_table(tbl, col_name):
    """
    Label training data

    Parameters
    ----------
    tbl : MTable, Table to be labeled
    col_name : String, Name of the label column

    Returns
    -------
    result : MTable, Table with labels

    Notes
    -----
    The label value is expected to be only 0 or 1.
    """
    from magellan.gui.mtable_gui import edit
    table = tbl.copy()
    if col_name in table.columns:
        logging.getLogger(__name__).warning('Input table already contains table with name %s' %col_name)
    else:
        table[col_name] = 0
    mg.edit(table)
    table[col_name] = table[col_name].astype(int)
    # check if the table contains only 0s and 1s
    c1 = table[col_name] == 1
    c2 = table[col_name] == 0
    c = sum(c1|c2)
    assert c == len(table), 'The label column contains values other than 0 and 1'

    table = MTable(table, key=tbl.get_key())
    table.properties = tbl.properties
    return table