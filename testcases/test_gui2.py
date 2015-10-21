from PyQt4.QtCore import *
from PyQt4.QtWidgets import *
from PyQt4.QtGui import *
import sys

class MainWindow(QMainWindow):

    def __init__(self,  parent=None):
        super(MainWindow,self).__init__(parent)

        self.initUI()

    def createGroup(self):
        groupBox = QGroupBox()

        self.treeWidget = QTreeWidget()

        header=QTreeWidgetItem(["Tree","First","secondo"])
        #...
        self.treeWidget.setHeaderItem(header)   #Another alternative is setHeaderLabels(["Tree","First",...])

        root = QTreeWidgetItem(self.treeWidget, ["root"])
        A = QTreeWidgetItem(root, ["A"])
        barA = QTreeWidgetItem(A, ["bar", "i", "ii"])
        bazA = QTreeWidgetItem(A, ["baz", "a", "b"])

        barA.setFlags(barA.flags() | Qt.ItemIsEditable)
        bazA.setFlags(bazA.flags() | Qt.ItemIsEditable)

        # switch off "default" editing behaviour
        # as it does not allow to configure only an individual
        # column as editable
        self.treeWidget.setEditTriggers(self.treeWidget.NoEditTriggers)

        # to be able to decide on your own whether a particular item
        # can be edited, connect e.g. to itemDoubleClicked
        self.treeWidget.itemDoubleClicked.connect(self.checkEdit)


        vbox = QVBoxLayout()
        vbox.addWidget(self.treeWidget)

        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    # in your connected slot, you can implement any edit-or-not-logic
    # you want
    def checkEdit(self, item, column):
    # e.g. to allow editing only of column 1:
        if column == 1:
            self.treeWidget.editItem(item, column)

    def initUI(self):
        self.resize(300, 220)

        self.grid = QGridLayout()

        self.widget = QWidget()
        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)
        self.grid.addWidget(self.createGroup(),1,0,1,2)

        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())