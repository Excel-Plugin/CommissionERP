import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtSql import *

from table_page import TablePage


class TableEditor(QMainWindow):
    addTabSignal = QtCore.pyqtSignal(object, name='AddTabSignal')

    def __init__(self):
        super(TableEditor, self).__init__()
        loadUi('table_editor.ui', self)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName('test.db')
        self.db.open()  # 开启数据库连接
        self.addTabSignal.connect(self.addTablePage)

    def addTablePage(self, condition):
        self.tabWidget.addTab(TablePage(self.db, 'saler', condition), "序时簿" + str(self.tabWidget.count() + 1))
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = TableEditor()
    myShow.show()
    sys.exit(app.exec_())
