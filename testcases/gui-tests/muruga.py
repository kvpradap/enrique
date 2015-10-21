from PyQt4 import QtGui, QtCore
from  magellan.utils.gui_utils import DictTableView, DictTableViewWithLabel, DataFrameTableView, \
    DataFrameTableViewWithLabel, TreeView, TreeViewWithLabel


class MainWindowManager(QtGui.QWidget):

    def __init__(self, dictionary, fp_dataframe, fn_dataframe):
        super(MainWindowManager, self).__init__()
        self.dictionary = dictionary
        self.fp_dataframe = fp_dataframe
        self.fn_dataframe = fn_dataframe
        self.metric_widget = None
        self.dataframe_widget = None
        self.combo_box = None
        self.current_combo_text = 'False Positives'
        self.current_dataframe = self.fp_dataframe
        self.setup_gui()

    def setup_gui(self):
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(['False Positives', 'False Negatives'])
        self.combo_box.activated[str].connect(self.combobox_onactivated)

        self.metric_widget = DictTableViewWithLabel(self, self.dictionary, 'Metrics',
                                                    self.combo_box)
        self.dataframe_widget = DataFrameTableViewWithLabel(self,
                                                            self.current_dataframe, self.current_combo_text)
        self.setWindowTitle('Debugger')
        layout = QtGui.QVBoxLayout(self)
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.metric_widget)
        splitter.addWidget(self.dataframe_widget)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def handle_debug_button(self, index):
        print 'Debug button clicked : ' + str(index)
        d1 = self.fp_dataframe.ix[1].to_dict()
        d2 = self.fn_dataframe.ix[2].to_dict()
        debug_obj = DebugWindowManager(d1, d2, d1)
        debug_obj.show()


    def handle_show_button(self, index):
        print 'Show button clicked : ' + str(index)
        d1 = self.fp_dataframe.ix[1].to_dict()
        d2 = self.fn_dataframe.ix[2].to_dict()
        show_obj = ShowWindowManager(d1, d2)
        show_obj.show()





    def combobox_onactivated(self, text):
        if text != self.current_combo_text:
            print text
            if text == 'False Negatives':
                self.current_combo_text = text
                self.current_dataframe = self.fn_dataframe
            else:
                self.current_combo_text = text
                self.current_dataframe = self.fp_dataframe
            self.dataframe_widget.tbl_obj.dataframe = self.current_dataframe
            self.dataframe_widget.tbl_obj.setup_gui()
            self.dataframe_widget.label_obj.setText(text)
            # self.dataframe_widget.setup_gui()


class ShowWindowManager(QtGui.QWidget):
    def __init__(self, left_tuple_dict, right_tuple_dict):
        super(ShowWindowManager, self).__init__()
        self.left_tuple_dict = left_tuple_dict
        self.right_tuple_dict = right_tuple_dict
        self.left_tuple_widget = None
        self.right_tuple_widget = None

        self.setup_gui()

    def setup_gui(self):
        self.left_tuple_widget = DictTableViewWithLabel(self, self.left_tuple_dict, 'Left Tuple')
        self.right_tuple_widget = DictTableViewWithLabel(self, self.right_tuple_dict, 'Right Tuple')
        self.setWindowTitle('Show Tuples')
        layout = QtGui.QVBoxLayout()
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.left_tuple_widget)
        splitter.addWidget(self.right_tuple_widget)
        layout.addWidget(splitter)
        self.setLayout(layout)



class DebugWindowManager(QtGui.QWidget):
    def __init__(self, left_tuple_dict, right_tuple_dict, d):
        super(DebugWindowManager, self).__init__()
        self.left_tuple_dict = left_tuple_dict
        self.right_tuple_dict = right_tuple_dict
        self.debug_result = d
        self.left_tuple_widget = None
        self.right_tuple_widget = None
        self.debug_widget = None
        self.setup_gui()

    def setup_gui(self):
        self.left_tuple_widget = DictTableViewWithLabel(self, self.left_tuple_dict, 'Left Tuple')
        self.right_tuple_widget = DictTableViewWithLabel(self, self.right_tuple_dict, 'Right Tuple')
        self.setWindowTitle('Debug Tuples')
        # self.debug_widget = DictTableViewWithLabel(self, self.debug_result, 'Debug Result')
        self.debug_widget = TreeViewWithLabel(self, "Tree details", type="dt")

        layout = QtGui.QHBoxLayout()
        splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter1.addWidget(self.left_tuple_widget)
        splitter1.addWidget(self.right_tuple_widget)

        splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.debug_widget)
        layout.addWidget(splitter2)
        self.setLayout(layout)


import magellan as mg
from collections import OrderedDict
app = mg._viewapp
dataframe = mg.load_dataset('table_A')
b = mg.load_dataset('table_B')
metric_data = OrderedDict()
metric_data['Precision'] = 0.95
metric_data['Recall'] = 0.93
metric_data['F1'] = 0.94
metric_data['Num. False Positives'] = 5
metric_data['Num. False Negatives'] = 6

m = MainWindowManager(metric_data, dataframe, b)
m.show()
app.exec_()

