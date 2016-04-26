import logging
import magellan as mg
from magellan.core.mtable import MTable
def label_table(tbl, col_name, replace=True):
    """
    Label training data

    Parameters
    ----------
    tbl : MTable, Table to be labeled
    col_name : String, Name of the label column
    replace : Boolean, specifies whether the column with the given 'col_name' must be overwritten, if it already exists.
    [This option is currently experimental].

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
        if replace == True:
            logging.getLogger(__name__).warning('Input table already contains column %s. '
                                                '' %col_name)
            table[col_name] = 0
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