import logging
import magellan as mg

def label(tbl, col_name):
    from magellan.gui.mtable_gui import edit
    table = tbl.copy()
    if col_name in table.columns:
        logging.getLogger(__name__).warning('Input table already contains table with name %s' %col_name)
    else:
        table[col_name] = 0
    mg.edit(table)
    table[col_name] = table[col_name].astype(int)
    table.properties = tbl.properties
    return table