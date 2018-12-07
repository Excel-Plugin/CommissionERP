import os
import sqlite3
import sys
import threading
import pythoncom
import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtSql import *

from table_page import TablePage
from InterfaceModule import Easyexcel


class TableEditor(QMainWindow):
    addTabSignal = QtCore.pyqtSignal(object, name='AddTabSignal')

    def __init__(self):
        super(TableEditor, self).__init__()
        loadUi('table_editor.ui', self)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName('test.db')
        self.db.open()  # 开启数据库连接
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTabPage)
        self.addTabSignal.connect(self.addTablePage)
        self.actionExportExcel.triggered.connect(self.exportExcelSlot)

    def addTablePage(self, info):
        table_name, condition, crossTable = info
        if crossTable:
            tab_name = "序时簿"
        else:
            tab_name = table_name
        self.tabWidget.addTab(TablePage(self.db, table_name, condition, crossTable), tab_name)
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
        self.show()

    def closeTabPage(self, index):
        self.tabWidget.removeTab(index)

    def exportExcelSlot(self):
        if self.tabWidget.count() <= 0:
            QMessageBox.warning(self, "没有表单", "当前没有可导出的表单")
            return
        filePath, _ = QFileDialog.getSaveFileName(self, "文件导出", ".", "Excel File (*.xlsx)")
        if filePath == '':  # 取消导出
            return
        elif os.path.exists(filePath):
            os.remove(filePath)
        filePath = filePath.replace('/', '\\')  # Excel不识别C:/xxx/xxx.xlsx的路径，只识别C:\xxx\xxx.xlsx
        self.tabWidget.currentWidget().exportToExcel(filePath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = TableEditor()
    myShow.show()
    sys.exit(app.exec_())
