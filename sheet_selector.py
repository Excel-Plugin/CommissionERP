from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHeaderView, QComboBox, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi


class SheetsComboBox(QComboBox):

    def __init__(self):
        super(SheetsComboBox, self).__init__()
        self.addItems(["不导入", "数据源表", "售后员表", "客户编号表", "规则表", "指导价表", "主管表", "业务员提成明细", "售后员提成明细"])


class SheetSelector(QDialog):

    def __init__(self, sheet_names, cur_tables: list):
        """cur_tables为当前数据库中已存在的数据表的列表"""
        super(SheetSelector, self).__init__()
        loadUi("sheet_selector.ui", self)
        self.__sheet_info = []  # 注意：sheet_info必须为列表，格式为[(Sheet名, 数据表类型, 数据表名称)]
        self.__cur_tables = cur_tables
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for sht in sheet_names:
            rowNumber = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowNumber)
            shtWidget = QTableWidgetItem(sht)
            shtWidget.setFlags(shtWidget.flags() & ~Qt.ItemIsEditable)  # 禁止Sheet名称修改
            self.tableWidget.setItem(rowNumber, 0, shtWidget)
            self.tableWidget.setCellWidget(rowNumber, 1, SheetsComboBox())

    def get_sheet_info(self):
        return self.__sheet_info

    def accept(self):
        indices = []  # 要导入的sheet相关信息
        existed_tables = set(self.__cur_tables)  # 已存在的数据表：包括数据库中已有的表和表单里填写的表名
        for i in range(0, self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i, 1).currentText() != '不导入':
                if self.tableWidget.item(i, 2) is None or self.tableWidget.item(i, 2).text() == '':
                    QMessageBox.warning(self, "表单不完整", "数据表名称有空值，无法导入")
                    return
                # 确保不会添加已存在的表名，且添加的表名之间不重复
                print(self.tableWidget.item(i, 2).text())
                if self.tableWidget.item(i, 2).text() in existed_tables:
                    QMessageBox.warning(self, "数据表名称已存在", f"数据表'{self.tableWidget.item(i, 2).text()}'已存在，不能重复添加")
                    return
                else:
                    existed_tables.add(self.tableWidget.item(i, 2).text())
                print(self.tableWidget.item(i, 2).text())
                indices.append(i)
        for i in indices:
            sheet_name = self.tableWidget.item(i, 0).text()
            table_type = self.tableWidget.cellWidget(i, 1).currentText()
            table_name = self.tableWidget.item(i, 2).text()
            self.__sheet_info.append((sheet_name, table_type, table_name))
        super(SheetSelector, self).accept()
