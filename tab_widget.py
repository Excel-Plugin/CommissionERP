from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QWidget, QFormLayout, QTableView, QGridLayout


class TabWidget(QWidget):

    def __init__(self, table_name):
        super(QWidget, self).__init__()
        self.model = QSqlTableModel(self)
        self.model.setTable(table_name)
        self.model.select()
        tableView = QTableView()
        tableView.setModel(self.model)
        layout = QGridLayout()
        layout.addWidget(tableView)
        self.setLayout(layout)
