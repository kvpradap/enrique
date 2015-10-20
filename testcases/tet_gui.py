from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pandas as pd
from functools import partial

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
        self._model = model

        self.setSortingEnabled(True)
        # self.horizontalHeader().setStretchLastSection(True)

        self.setColumnCount(len(model.getDataFrame().columns) + 2)
        self.setRowCount(len(model.getDataFrame()))

        headers = ['Show', 'Debug']
        headers.extend(list(self._model.getDataFrame().columns.values))

        self.setHorizontalHeaderLabels(headers)

        # self.setColumnWidth(0, 35)

        self.verticalHeader().setVisible(True)

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

    def handle_show_button(self, index):
        x = 20

        print 'show button clicked : ' + str(index)


class MWidget(QWidget):
    def __init__(self, data):
        super(MWidget, self).__init__()
        model = DataModel(data)
        view = MTableView(model)

        # set window size
        width = min((len(data.columns) + 1)*105, mg._viewapp.desktop().screenGeometry().width() - 50)
        height = min((len(data) + 1)*41, mg._viewapp.desktop().screenGeometry().width() - 100)
        self.resize(width, height)

        # set window title
        self.setWindowTitle("Debug - Mtable")

        layout = QGridLayout()
        layout.addWidget(view, 0, 0)
        self.setLayout(layout)
        QApplication.setStyle(QStyleFactory.create('motif'))


import magellan as mg

d = mg.load_dataset('table_A')
w = MWidget(d)
w.show()

mg._viewapp.instance().exec_()



