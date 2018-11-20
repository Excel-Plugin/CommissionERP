from PyQt5.QtWidgets import QDialog, QHeaderView, QComboBox, QTableWidgetItem
from PyQt5.uic import loadUi


class SheetsComboBox(QComboBox):

    def __init__(self):
        super(SheetsComboBox, self).__init__()
        self.addItems(["不导入", "数据源表", "售后员表", "客户编号表", "规则表", "指导价表", "主管表", "业务员提成明细", "售后员提成明细"])


class SheetSelector(QDialog):

    def __init__(self, sheet_names):
        super(SheetSelector, self).__init__()
        loadUi("sheet_selector.ui", self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for sht in sheet_names:
            rowNumber = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowNumber)
            self.tableWidget.setItem(rowNumber, 0, QTableWidgetItem(sht))
            self.tableWidget.setCellWidget(rowNumber, 1, SheetsComboBox())
