import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *

from Widget import Widget


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('./test.db')
        if db.open():
            print("db is open")
        # self.model = QSqlTableModel(self)
        # self.model.setTable('after_saler')
        # self.model.select()
        loadUi('MainWindow.ui', self)
        # self.tableView.setModel(self.model)
        self.tabWidget.addTab(Widget('after_saler'), "数据源表")
        self.tabWidget.addTab(Widget('after_saler'), "售后员表")
        self.tabWidget.addTab(Widget('after_saler'), "客户编号表")
        self.tabWidget.addTab(Widget('after_saler'), "规则表")
        self.tabWidget.addTab(Widget('after_saler'), "主管表")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = MainWindow()
    myShow.show()
    sys.exit(app.exec_())
