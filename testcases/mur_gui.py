import sys
import magellan as mg
from PyQt4 import QtGui, QtCore

edit_flag = False

#data = {'col1':['1','2','3'], 'col2':['4','5','6'], 'col3':['7','8','9']}

# tbl = mg.load_dataset('table_A')
# datatable = QtGui.QTableWidget()
#
# # disable edit
# if edit_flag == False:
#     datatable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
#
# datatable.setRowCount(len(tbl.index))
# datatable.setColumnCount(len(tbl.columns))
#
# # set data
# for i in range(len(tbl.index)):
#     for j in range(len(tbl.columns)):
#         datatable.setItem(i, j, QtGui.QTableWidgetItem(str(tbl.iget_value(i, j))))
#
# list_col = list(tbl.columns.values)
# datatable.setHorizontalHeaderLabels(list_col)
#
# # set window size
# width = min((j + 1)*105, mg._viewapp.desktop().screenGeometry().width() - 50)
# height = min((i + 1)*41, mg._viewapp.desktop().screenGeometry().width() - 100)
# datatable.resize(width, height)
#
# # set window title
# datatable.setWindowTitle("Mtable")
#
# # show window
# datatable.show()
# mg._viewapp.exec_()




class MurTable(QtGui.QTableWidget):

    def __init__(self, data):
        self.data = data
        super(MurTable, self).__init__()
        self.init_gui()
        print 'returning from init gui'

    def init_gui(self):
        nrows = len(self.data.index)
        ncols = len(self.data.columns)

        self.setRowCount(nrows)
        self.setColumnCount(ncols)
        self.setHorizontalHeaderLabels(list(self.data.columns))

        for i in range(nrows):
            for j in range(ncols):
                self.setItem(i, j, QtGui.QTableWidgetItem(str(self.data.iget_value(i, j))))


        width = min((j + 1)*105, mg._viewapp.desktop().screenGeometry().width() - 50)
        height = min((i + 1)*41, mg._viewapp.desktop().screenGeometry().width() - 100)
        self.resize(width, height)











data = mg.load_dataset('table_A')
table = QtGui.QTableWidget()
table = MurTable(data)
table.show()
mg._viewapp.exec_()

