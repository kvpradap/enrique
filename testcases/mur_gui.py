"""
ZetCode PyQt4 tutorial

This example shows
how to use QtGui.QSplitter widget.

author: Jan Bodnar
website: zetcode.com
last edited: September 2011
"""

import sys
from PyQt4 import QtGui, QtCore

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        hbox = QtGui.QHBoxLayout(self)

        # topleft = QtGui.QFrame(self)
        # topleft.setFrameShape(QtGui.QFrame.StyledPanel)

        topleft = QtGui.QTableWidget()
        topleft1 = QtGui.QComboBox()
        topleft1.addItems(['FP', 'FN'])
        # topleft1 = QtGui.QTableWidget()
        # topright = QtGui.QFrame(self)
        # topright.setFrameShape(QtGui.QFrame.StyledPanel)

        # bottom = QtGui.QFrame(self)
        # bottom.setFrameShape(QtGui.QFrame.StyledPanel)
        bottom = QtGui.QTableWidget()

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topleft1)

        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(bottom)

        hbox.addWidget(splitter2)
        self.setLayout(hbox)
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('QtGui.QSplitter')
        self.show()

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()