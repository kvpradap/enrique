from functools import partial
from PyQt4 import QtGui, QtCore, Qt
import pandas as pd


class MainWindowManager(QtGui.QWidget):

    def __init__(self, dictionary, fp_dataframe, fn_dataframe):
        super(MainWindowManager, self).__init__()
        self.dictionary = dictionary
        self.fp_dataframe = fp_dataframe
        self.fn_dataframe = fn_dataframe
        self.metric_widget = None
        self.dataframe_widget = None
        self.combo_box = None
        self.setup_gui()

    def setup_gui(self):
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(['False Positives', 'False Negatives'])
        self.combo_box.activated[str].connect(self.combobox_onactivated)

        self.metric_widget = DictTableViewWithLabel(self, self.dictionary, 'Metrics',
                                                    self.combo_box)
        self.dataframe_widget = DataFrameTableViewWithLabel(self,
                                                            self.fp_dataframe, 'False Postives')
        self.setWindowTitle('Debugger')
        layout = QtGui.QVBoxLayout(self)
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.metric_widget)
        splitter.addWidget(self.dataframe_widget)
        layout.addWidget(splitter)
        self.setLayout(layout)





    def handle_debug_button(self, index):
        print 'Debug button clicked : ' + str(index)
    def handle_show_button(self, index):
        print 'Show button clicked : ' + str(index)
    def combobox_onactivated(self, text):
        print text + "is on"

class DataFrameTableView(QtGui.QTableWidget):
    def __init__(self, controller, dataframe):
        super(DataFrameTableView, self).__init__()
        self.controller = controller
        self.dataframe = dataframe
        self.setup_gui()

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe

    def setup_gui(self):
        # set rowcount
        nrows = len(self.dataframe)
        self.setRowCount(nrows)
        # set col count
        ncols = len(self.dataframe.columns)
        self.setColumnCount(ncols + 2) # + 2 because of show and debug icons

        # set headers
        # horiz. header
        headers = ['Show', 'Debug']
        headers.extend(list(self.dataframe.columns))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setStretchLastSection(True)
        # vertic. header
        self.verticalHeader().setVisible(True)

        # populate data
        for i in range(nrows):
            for j in range(ncols + 2):
                if j == 0:
                    button = QtGui.QPushButton('Show', self)
                    self.setCellWidget(i, j, button)
                    button.clicked.connect(partial(self.controller.handle_show_button, i))
                elif j == 1:
                    button = QtGui.QPushButton('Debug', self)
                    self.setCellWidget(i, j, button)
                    button.clicked.connect(partial(self.controller.handle_debug_button, i))
                else:
                    if pd.isnull(self.dataframe.iloc(i, j - 2)):
                        self.setItem(i, j, QtGui.QTableWidgetItem(""))
                    else:
                        self.setItem(i, j, QtGui.QTableWidgetItem(
                            str(self.dataframe.iloc[i, j - 2])
                        ))
                    self.item(i, j).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)




class DataFrameTableViewWithLabel(QtGui.QWidget):
    def __init__(self, controller, dataframe, label):
        super(DataFrameTableViewWithLabel, self).__init__()
        self.dataframe = dataframe
        self.label = label
        self.controller = controller
        self.setup_gui()

    def set_dataframe(self, data_frame):
        self.dataframe = data_frame

    def set_label(self, label):
        self.label = label

    def setup_gui(self):
        label = QtGui.QLabel(self.label)
        tbl_view = DataFrameTableView(self.controller, self.dataframe)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(tbl_view)
        self.setLayout(layout)

class DictTableViewWithLabel(QtGui.QWidget):
    def __init__(self, controller, dictionary, label, combo_box=None):
        super(DictTableViewWithLabel, self).__init__()
        self.dictionary = dictionary
        self.label = label
        self.controller = controller
        self.combo_box = combo_box
        self.setup_gui()

    def setup_gui(self):
        label = QtGui.QLabel(self.label)
        dict_view = DictTableView(self.controller, self.dictionary,
                                  self.combo_box)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(dict_view)
        self.setLayout(layout)



class DictTableView(QtGui.QTableWidget):
    def __init__(self, controller, dictionary, combo_box=None):
        super(DictTableView, self).__init__()
        self.controller = controller
        self.dictionary = dictionary
        self.combo_box = combo_box
        self.setup_gui()


    def set_dictionary(self, dictionary):
        self.dictionary = dictionary

    def setup_gui(self):
        #sorting
        self.setSortingEnabled(True)
        self.setColumnCount(1)

        #nrows
        nrows = len(self.dictionary.keys())
        if self.combo_box is not None:
            nrows += 1
        self.setRowCount(nrows)

        # horizontal headers
        self.setHorizontalHeaderLabels(['Value'])
        self.horizontalHeader().setStretchLastSection(True)

        # vertical headers
        h = self.dictionary.keys()
        h.append('Show')
        self.setVerticalHeaderLabels(h)

        idx = 0

        for k, v in self.dictionary.iteritems():
            self.setItem(idx, 0, QtGui.QTableWidgetItem(str(v)))
            idx += 1
        if self.combo_box is not None:
            self.setCellWidget(idx, 0, self.combo_box)


import magellan as mg
from collections import OrderedDict
app = mg._viewapp
dataframe = mg.load_dataset('table_A')
metric_data = OrderedDict()
metric_data['Precision'] = 0.95
metric_data['Recall'] = 0.93
metric_data['F1'] = 0.94
metric_data['Num. False Positives'] = 5
metric_data['Num. False Negatives'] = 6

m = MainWindowManager(metric_data, dataframe, dataframe)
m.show()
app.exec_()

