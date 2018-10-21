import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *

from table_page import TablePage


class TableEditor(QMainWindow):
    addTabSignal = QtCore.pyqtSignal(object, name='AddTabSignal')

    def __init__(self):
        super(TableEditor, self).__init__()
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('test.db')
        loadUi('table_editor.ui', self)
        self.addTabSignal.connect(self.addTabWidget)

    def addTabWidget(self, condition):
        self.tabWidget.addTab(TablePage('saler', condition), "序时簿" + str(self.tabWidget.count() + 1))
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = TableEditor()
    myShow.show()
    sys.exit(app.exec_())
