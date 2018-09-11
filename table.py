import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QHeaderView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('./test.db')
        if db.open():
            print("db is open")
        self.model = QSqlTableModel(self)
        self.model.setTable('after_saler')
        self.model.setHeaderData(0, Qt.Horizontal, QVariant("编号"))
        self.model.setHeaderData(1, Qt.Horizontal, QVariant("姓名"))
        self.model.setHeaderData(2, Qt.Horizontal, QVariant("出货地点"))
        self.model.select()
        loadUi('table.ui', self)
        # self.tableView.setStyleSheet("""
        #     QTableCornerButton::section{
        #         background-color: #258cca;
        #         border:0px;
        #         color: white;
        #     }
        #     QTableView{
        #         selection-background-color: rgb(128, 128, 128);
        #     }
        # """)
        # self.tableView.verticalHeader().setStyleSheet("""
        #     QHeaderView::section{
        #         background-color: #f89045;
        #         width: 50px;
        #         color: white;
        #         font-size: 16px;
        #         font-weight: bold;
        #         /*border: 1px solid rgb(229,229,229);*/
        #         /*border-bottom-color: rgb(229,229,229);*/
        #         border-bottom: 1px solid white;
        #         font-family: Microsoft YaHei;
        #     }
        # """)
        # self.tableView.horizontalHeader().setStyleSheet("""
        #     QHeaderView::section{
        #         background-color: #f89045;
        #         /*border: 1px solid white;*/
        #         border-right-radius: 1px;
        #         border-right-color: white;
        #         font-size: 16px;
        #         font-weight: bold;
        #         color: white;
        #         font-family: Microsoft YaHei;
        #     }
        # """)
        # self.findChild(QtWidgets.QAbstractButton).setText("TEXT")
        self.tableView.setModel(self.model)
        # self.tableView.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = MyWindow()
    myShow.show()
    sys.exit(app.exec_())
