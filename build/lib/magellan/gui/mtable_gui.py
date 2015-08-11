import logging
from PyQt4 import QtGui

logger = logging.getLogger(__name__)

# contain basic routines to view and edit table -- should be updated with leon's code

# view table
def view(tbl, edit_flag=False):
    app = QtGui.QApplication([])
    datatable = QtGui.QTableWidget()

    # disable edit
    if edit_flag is False:
        datatable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    datatable.setRowCount(len(tbl.index))
    datatable.setColumnCount(len(tbl.columns))

    # set data
    for i in range(len(tbl.index)):
        for j in range(len(tbl.columns)):
            datatable.setItem(i, j, QtGui.QTableWidgetItem(str(tbl.iget_value(i, j))))

    list_col = list(tbl.columns.values)
    datatable.setHorizontalHeaderLabels(list_col)

    # set window size
    width = min((j + 1)*105, app.desktop().screenGeometry().width() - 50)
    height = min((i + 1)*41, app.desktop().screenGeometry().width() - 100)
    datatable.resize(width, height)

    # set window title
    datatable.setWindowTitle("Mtable")

    # show window
    datatable.show()
    app.exec_()
    #app.deleteLater()
    app.exit(0)
    if edit_flag:
        return datatable

# edit table
def edit(tbl):
    datatable = view(tbl, edit_flag=True)
    cols = list(tbl.columns)
    idxv = list(tbl.index)
    for i in range(len(tbl.index)):
        for j in range(len(tbl.columns)):
            val = datatable.item(i, j).text()
            inp = tbl.iget_value(i, j)
            val = cast_val(val, inp)
            tbl.set_value(idxv[i], cols[j], val)


# need to cast string values from edit window
def cast_val(v, i):
    if v == "None":
        return None
    elif isinstance(i, bool):
        return bool(v)
    elif isinstance(i, float):
        return float(v)
    elif isinstance(i, int):
        return int(v)
    elif isinstance(i, basestring):
        return str(v)
    elif isinstance(i, object):
        return v
    else:
        logger.warning('Input value did not match any of the known types')
        return v