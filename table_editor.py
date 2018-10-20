import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *

from tab_widget import TabWidget


class TableEditor(QMainWindow):

    def __init__(self):
        super(TableEditor, self).__init__()
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('./test.db')
        if db.open():
            print("db is open")
        # self.model = QSqlTableModel(self)
        # self.model.setTable('test')
        # self.model.select()
        loadUi('table_editor.ui', self)
        # self.tableView.setModel(self.model)
        # self.tabWidget.addTab(TabWidget('saler'), "业务员提成明细序时簿1")

    def addTabWidget(self, condition):
        self.tabWidget.addTab(TabWidget('saler'), "业务员提成明细序时簿1")
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = TableEditor()
    myShow.show()
    sys.exit(app.exec_())
