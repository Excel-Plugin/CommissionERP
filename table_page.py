import threading

import pythoncom
from PyQt5 import QtSql, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlQueryModel
from PyQt5.QtWidgets import QWidget, QFormLayout, QTableView, QGridLayout, QApplication, QMessageBox
import logging

from InterfaceModule import Easyexcel
from data_manager import DataManager
from excel_check import ExcelCheck


class TablePage(QWidget):
    exportSignal = QtCore.pyqtSignal(object)

    def __init__(self, db, table_name, condition, crossTable=False):
        """当crossTable为False时，为单张表查看，可读可写，table_name为表名，condition为过滤条件
        当crossTable为True时，为同类型多张表查询，只可以读不可以写，table_name为表类型名，condition为过滤条件"""
        super(QWidget, self).__init__()
        self.exportSignal.connect(self.exportSlot)
        self.db = db
        if self.db.open():  # 开启数据库连接
            logging.info("db is open")
        else:
            logging.critical("db is not open!!!")
            err = self.db.lastError()
            logging.critical(err.text())
            logging.critical(QtSql.QSqlDatabase.drivers())
            logging.critical(QApplication.libraryPaths())
        self.__table_name = table_name
        self.__crossTable = crossTable
        self.__dm = DataManager()
        if crossTable:
            self.model = QSqlQueryModel(self)
            for section, value in enumerate(['id']+ExcelCheck.headers[table_name]):  # 设置表头为该类型表的表头，包括id
                self.model.setHeaderData(section, Qt.Horizontal, value)
            if condition == "":
                query = " union ".join(
                    [f"select * from {t}" for t in self.__dm.get_my_tables(table_name)])
            else:
                query = " union ".join(
                    [f"select * from {t} where {condition}" for t in self.__dm.get_my_tables(table_name)])
            print(query)
            try:
                self.model.setQuery(query, self.db)
            except Exception as e:
                logging.exception(e)
                QMessageBox.warning(self, "查询出错", str(e))
        else:
            self.model = QSqlTableModel(self, db=self.db)
            self.model.setTable(table_name)
            self.model.setFilter(condition)
            self.model.select()
        tableView = QTableView()
        tableView.setModel(self.model)
        layout = QGridLayout()
        layout.addWidget(tableView)
        self.setLayout(layout)

    def exportToExcel(self, filePath):
        # 填写表头list
        if self.__crossTable:
            header = ["id"] + ExcelCheck.headers[self.__table_name]  # 在前面加上id列
        else:
            header = self.__dm.get_column_names(table_name=self.__table_name)
        # 确定s_num集合
        s_num = set()
        for i, name in enumerate(header):
            if name in ["发票号码"]:  # 属于s_num的列
                s_num.add(i)
        # 填写表格内容二维数组
        content = [["" for c in range(self.model.columnCount())] for r in range(self.model.rowCount())]
        for i in range(self.model.rowCount()):
            for j in range(self.model.columnCount()):
                content[i][j] = self.model.index(i, j).data()
        print(header)
        print(content)
        logging.info("正在启动子线程")
        # 设置成为守护主线程，主线程退出后子线程直接销毁不再执行子线程的代码
        threading.Thread(target=self.writeToExcelWork, args=(filePath, header, content, s_num), daemon=True).start()

    def writeToExcelWork(self, filePath, header, content, s_num):
        try:
            logging.info("子线程已启动，正在调用Easyexcel进行导出")
            pythoncom.CoInitialize()
            excel = Easyexcel(filepath=filePath, visible=False)
            logging.info("Easyexcel对象创建成功，正在写入")
            excel.set_sheet("Sheet1", header, content, s_num)
            logging.info("数据写入完成，正在关闭Easyexcel对象")
            excel.close()
            logging.info("Easyexcel已正常关闭")
            self.exportSignal.emit("文件已导出，路径为"+filePath)
        except Exception as e:
            logging.exception(e)
            self.exportSignal.emit(e)

    def exportSlot(self, info):
        if isinstance(info, str):
            QMessageBox.information(self, "文件已导出", info)
        elif isinstance(info, Exception):
            QMessageBox.warning(self, "文件导出出错", str(info))
