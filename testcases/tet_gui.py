from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pandas as pd
from functools import partial
import magellan as mg
from collections import OrderedDict

class DataModel():
    def __init__(self, df):
        self.dataframe = df

    def getDataFrame(self):
        """ Returns reference to the dataframe.
        Args:
        Returns:
            Reference to the dataframe.
        """

        return self.dataframe

    def setDataFrame(self, df):
        """ Change the dataframe attribute to reference new dataframe.
        Args:
            The new dataframe the model will use.
        Returns:
        """

        self.dataframe = df

class MTableView(QTableWidget):
    def __init__(self, model, *args):
        super(MTableView, self).__init__(*args)
        self.set_model(model)
        self.paint_gui()

    def set_model(self, model):
        self._model = model

    def paint_gui(self):
        # enable sorting.
        self.setSortingEnabled(True)
        self.setColumnCount(len(self._model.getDataFrame().columns) + 2)
        self.setRowCount(len(self._model.getDataFrame()))

        headers = ['Show', 'Debug']
        headers.extend(list(self._model.getDataFrame().columns.values))

        self.setHorizontalHeaderLabels(headers)

        # self.setColumnWidth(0, 35)

        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setStretchLastSection(True)

        for i in range(len(self._model.getDataFrame().index)):
            for j in range(len(self._model.getDataFrame().columns) + 2) :
                if j == 0:
                    button = QPushButton('Show', self)
                    self.setCellWidget(i, j, button)
                    button.clicked.connect(partial(self.handle_show_button, i))
                elif j == 1:
                    button = QPushButton('Debug', self)
                    self.setCellWidget(i, j, button)
                    button.clicked.connect(partial(self.handle_debug_button, i))

                else:

                    # self.setItem(i, j, QTableWidgetItem("pp"))
                    if pd.isnull(self._model.getDataFrame().iloc(i, j - 2)):
                        self.setItem(i, j, QTableWidgetItem(""))
                    else:
                        self.setItem(i, j, QTableWidgetItem(
                            str(self._model.getDataFrame().iloc[i, j - 2])))



    def handle_debug_button(self, index):
        y = 10
        print 'Debug button clicked : ' + str(index)
        d = mg.load_dataset('table_B')
        model = DataModel(d)
        view = MTableView(model)

        view.show()


    def handle_show_button(self, index):
        x = 20

        print 'show button clicked : ' + str(index)

class MetricWidget(QTableWidget):
    def __init__(self, model, *args):
        super(MetricWidget, self).__init__(*args)
        self.set_model(model)
        self.paint_gui()


    def set_model(self, model):
        self._model = model


    def paint_gui(self):
        self.setSortingEnabled(True)
        self.setColumnCount(1)
        self.setRowCount(len(self._model.keys())+1)
        headers = ['Value']
        #headers.extend(list(self._model.getDataFrame().columns.values))
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().setVisible(True)
        h = self._model.keys()
        h.append('Show')
        self.setVerticalHeaderLabels(h)
        self.horizontalHeader().setStretchLastSection(True)
        idx = 0

        for k, v in self._model.iteritems():
            self.setItem(idx, 0, QTableWidgetItem(str(v)))
            idx += 1
        b = QComboBox()
        b.addItems(['False Positives', 'False Negatives'])
        b.activated[str].connect(self.onActivated)
        self.setCellWidget(idx, 0, b)



    def onActivated(self, text):
        print text + " is on"




class MCombobox(QComboBox):
    def __init__(self):
        super(MCombobox, self).__init__()
        self.initUI()
    def initUI(self):
        print 'inside init'
        self.addItems(['False Positives', 'False Negatives'])
        self.activated[str].connect(self.onActivated)



class MurWidget(QWidget):
    def __init__(self, d):
        super(MurWidget, self).__init__()
        self.model = DataModel(d)
        self.view = MTableView(self.model)
        self.setWindowTitle("Debug - Mtable")
        metric_data = OrderedDict()
        metric_data['Precision'] = 0.95
        metric_data['Recall'] = 0.93
        metric_data['F1'] = 0.94
        metric_data['Num. False Positives'] = 5
        metric_data['Num. False Negatives'] = 6

        metric_table = MetricWidget(metric_data)
        hbox = QVBoxLayout(self)
        splitter2 = QSplitter(Qt.Horizontal)

        splitter2.addWidget(metric_table)
        splitter2.addWidget(self.view)
        hbox.addWidget(splitter2)
        self.setLayout(hbox)



class MWidget(QWidget):
    def __init__(self, d):
        super(MWidget, self).__init__()
        self.model = DataModel(d)
        self.view = MTableView(self.model)

        # # set window size
        # width = min((len(self.model.getDataFrame().columns) + 2)*105, mg._viewapp.desktop().screenGeometry().width() - 50)
        # height = min((len(self.model.getDataFrame()) + 2)*41, mg._viewapp.desktop().screenGeometry().width() - 100)
        # self.resize(width, height)

        # set window title
        self.setWindowTitle("Debug - Mtable")

        # change_btn = QPushButton('Change', self)

        # change_btn.clicked.connect(self.change_table_contents)
        metric_data = OrderedDict()
        metric_data['Precision'] = 0.95
        metric_data['Recall'] = 0.93
        metric_data['F1'] = 0.94
        metric_data['Num. False Positives'] = 5
        metric_data['Num. False Negatives'] = 6

        metric_table = MetricWidget(metric_data)
        combobox = MCombobox()
        hlayout = QVBoxLayout()
        hlayout.addWidget(metric_table)
        # hlayout.addWidget(combobox)




        # layout = QGridLayout()
        # layout.addWidget(change_btn, 0, 0)
        layout = QVBoxLayout()
        # layout.addWidget(metric_table, 0, 0)
        # layout.addWidget(self.view, 1, 0)
        # layout.addWidget(metric_table)
        layout.addLayout(hlayout)
        layout.addWidget(self.view)
        self.setLayout(layout)
        # QApplication.setStyle(QStyleFactory.create('motif'))

    def change_table_contents(self):
        d = mg.load_dataset('table_B')
        self.model = DataModel(d)
        self.view.set_model(self.model)
        self.view.paint_gui()
        # model = DataModel(d)
        # view = MTableView(model)

        # view.show()






import magellan as mg
import sys
app = mg._viewapp
d = mg.load_dataset('table_A')
# w = MWidget(d)
w = MurWidget(d)
w.show()

(app.exec_())



