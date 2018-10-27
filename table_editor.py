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
    exportFinishSignal = QtCore.pyqtSignal(object, name='exportFinishSignal')

    def __init__(self):
        super(TableEditor, self).__init__()
        loadUi('table_editor.ui', self)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName('test.db')
        self.db.open()  # 开启数据库连接
        self.addTabSignal.connect(self.addTablePage)
        self.actionExportExcel.triggered.connect(self.exportExcelSlot)
        self.exportFinishSignal.connect(self.exportFinishSlot)

    def addTablePage(self, condition):
        self.tabWidget.addTab(TablePage(self.db, 'saler', condition), "序时簿" + str(self.tabWidget.count() + 1))
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
        self.show()

    def exportExcelSlot(self):
        if self.tabWidget.count() <= 0:
            QMessageBox.warning(self, "没有表单", "当前没有可导出的表单")
            return
        filePath, _ = QFileDialog.getSaveFileName(self, "文件导出", ".", "Excel File (*.xlsx)")
        filePath = filePath.replace('/', '\\')  # Excel不识别C:/xxx/xxx.xlsx的路径，只识别C:\xxx\xxx.xlsx
        cursor = sqlite3.connect("test.db").cursor()
        cursor.execute('pragma table_info(saler)')
        columns = cursor.fetchall()
        header = [c[1] for c in columns]
        sql = 'select * from saler '
        if self.tabWidget.currentWidget().condition != '':
            sql += ' where ' + self.tabWidget.currentWidget().condition
        cursor.execute(sql)
        content = cursor.fetchall()
        logging.info("正在创建导出子线程")
        thread = threading.Thread(target=self.writeToExcel, args=(filePath, header, content), daemon=True)  # 设置成为守护主线程，主线程退出后子线程直接销毁不再执行子线程的代码
        logging.info("正在启动子线程")
        thread.start()
        self.statusBar().showMessage("正在导出")

    def writeToExcel(self, filePath, header, content):
        logging.info("子线程已启动，正在调用Easyexcel进行导出")
        pythoncom.CoInitialize()
        excel = Easyexcel(filepath=filePath, visible=False)
        logging.info("Easyexcel对象创建成功，正在写入")
        excel.set_sheet("Sheet1", header, content)
        logging.info("数据写入完成，正在关闭Easyexcel对象")
        excel.close()
        logging.info("Easyexcel已正常关闭")
        self.statusBar().showMessage("文件已导出至"+filePath)
        self.exportFinishSignal.emit("文件已导出，路径为"+filePath)

    def exportFinishSlot(self, message):
        QMessageBox.information(self, "文件已导出", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = TableEditor()
    myShow.show()
    sys.exit(app.exec_())
