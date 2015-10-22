from PyQt4 import QtGui, QtCore
from collections import OrderedDict
import pandas as pd
import magellan as mg

from  magellan.gui.gui_utils import DictTableViewWithLabel, DataFrameTableViewWithLabel, TreeViewWithLabel


class MainWindowManager(QtGui.QWidget):

    def __init__(self, dictionary, table, fp_dataframe, fn_dataframe):
        super(MainWindowManager, self).__init__()
        self.dictionary = dictionary
        self.table = table
        self.fp_dataframe = fp_dataframe
        self.fn_dataframe = fn_dataframe

        ltable = self.table.get_property('ltable')
        rtable = self.table.get_property('rtable')
        l_df = ltable.to_dataframe()
        r_df = rtable.to_dataframe()
        self.l_df = l_df.set_index(ltable.get_key(), drop=False)
        self.r_df = r_df.set_index(rtable.get_key(), drop=False)
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
        r = self.current_dataframe.ix[index]
        l_fkey = self.table.get_property('foreign_key_ltable')
        r_fkey = self.table.get_property('foreign_key_rtable')
        l_val = r[l_fkey]
        r_val = r[r_fkey]
        d1 = OrderedDict(self.l_df.ix[l_val])
        d2 = OrderedDict(self.r_df.ix[r_val])
        debug_obj = DebugWindowManager(d1, d2, d1)
        debug_obj.show()


    def handle_show_button(self, index):
        print 'Show button clicked : ' + str(index)
        r = self.current_dataframe.ix[index]
        l_fkey = self.table.get_property('foreign_key_ltable')
        r_fkey = self.table.get_property('foreign_key_rtable')
        l_val = r[l_fkey]
        r_val = r[r_fkey]
        d1 = OrderedDict(self.l_df.ix[l_val])
        d2 = OrderedDict(self.r_df.ix[r_val])
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



def vis_debug_dt(matcher, summary_stats, table, exclude_attrs, feat_table):
    metric = get_metric(summary_stats)
    fp_dataframe = get_dataframe(table, summary_stats['false_pos_ls'])
    fn_dataframe = get_dataframe(table, summary_stats['false_neg_ls'])
    app = mg._viewapp
    m = MainWindowManager(metric, table, fp_dataframe, fn_dataframe)
    m.show()
    app.exec_()




def get_metric(summary_stats):
    d = OrderedDict()
    keys = summary_stats.keys()
    mkeys = [k for k in keys if k not in ['false_pos_ls', 'false_neg_ls']]
    for k in mkeys:
        d[k] = summary_stats[k]
    return d

def get_dataframe(table, ls):
    df = table.to_dataframe()
    ret = pd.DataFrame(columns=table.columns.values)
    if len(ls) > 0:
        l_fkey = table.get_property('foreign_key_ltable')
        r_fkey = table.get_property('foreign_key_rtable')
        df = df.set_index([l_fkey, r_fkey], drop=False)
        d = df.ix[ls]
        ret = d
        ret.reset_index(inplace=True, drop=True)
    return ret


