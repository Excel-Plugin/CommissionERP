from PyQt5 import QtSql
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtWidgets import QWidget, QFormLayout, QTableView, QGridLayout, QApplication
import logging


class TablePage(QWidget):

    def __init__(self, db, table_name, condition):
        super(QWidget, self).__init__()
        self.db = db
        if self.db.open():  # 开启数据库连接
            logging.info("db is open")
        else:
            logging.critical("db is not open!!!")
            err = self.db.lastError()
            logging.critical(err.text())
            logging.critical(QtSql.QSqlDatabase.drivers())
            logging.critical(QApplication.libraryPaths())
        self.condition = condition
        self.model = QSqlTableModel(self, db=self.db)
        self.model.setTable(table_name)
        self.model.setFilter(self.condition)
        self.model.select()
        tableView = QTableView()
        tableView.setModel(self.model)
        layout = QGridLayout()
        layout.addWidget(tableView)
        self.setLayout(layout)
