import os
import sqlite3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QApplication, QHeaderView, \
    QTableView, QAbstractItemView, QComboBox, QTableWidgetItem, QFileDialog, QDialog
from PyQt5.uic import loadUi
import resources
from InterfaceModule import Easyexcel
from sheet_selector import SheetSelector
from table_editor import TableEditor


class LogicWidget(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems(["并且", "或者"])


cursor = sqlite3.connect("test.db").cursor()
cursor.execute('pragma table_info(salesman)')
columns = cursor.fetchall()
columnType = {c[1]: c[2] for c in columns}


class NameWidget(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems([c[1] for c in columns])


class CompWidget(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems(["等于", "不等于", "大于", "大于或等于", "小于", "小于或等于", "包含", "不包含", "为空值", "不为空值"])

    def getCondition(self, name, value):
        if 'text' in columnType[name]:  # 注意：若使用了其他的文本数据类型，这里需要更改
            value = "'" + value + "'"
        conditionDict = {"等于": name+" = "+value, "不等于": name+" != "+value,
                         "大于": name+" > "+value, "大于或等于": name+" >= "+value,
                         "小于": name+" < "+value, "小于或等于": name+" <= "+value,
                         # 注意：若关系为“包含”，则name必定为字符串相关类型，则value必定会两侧加''，所以下面需要去掉
                         "包含": name+" like '%"+value[1:-1]+"%' ", "不包含": name+"not like '%"+value[1:-1]+"%' ",
                         "为空值": name+" is null ", "不为空值": name+" is not null "
                         }
        return conditionDict[self.currentText()]


class ManageWidget(QWidget):
    conditionRow = {'logic': 0, 'name': 2, 'comp': 3, 'value': 4}

    def __init__(self, addTabSignal):
        super(ManageWidget, self).__init__()
        loadUi('manage_widget.ui', self)
        self.addTabSignal = addTabSignal
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.tableManagePushButton.setChecked(True)
        self.tableManagePushButton.clicked.connect(self.tableManagePushButtonClickedSlot)
        self.tableGeneratePushButton.setChecked(False)
        self.tableGeneratePushButton.clicked.connect(self.tableGeneratePushButtonClickedSlot)
        self.tableViewPushButton.setChecked(False)
        self.tableViewPushButton.clicked.connect(self.tableViewPushButtonClickedSlot)
        self.stackedWidget.setCurrentIndex(0)
        # 业务表管理page0
        self.importPushButton.clicked.connect(self.importPushButtonClickedSlot)
        self.listTableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.listTableWidget.horizontalHeader().setDefaultSectionSize(250)
        self.listTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 序时簿查看page2
        self.conditionTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.conditionTableWidget.removeRow(0)
        self.addConditionPushButton.clicked.connect(self.addRowToConditionTableWidget)
        self.deleteConditionPushButton.clicked.connect(self.removeRowFromConditionTableWidget)
        self.condTableGenPushButton.clicked.connect(self.condTableGenPushButtonClickedSlot)

    def addRowToConditionTableWidget(self):
        rowNumber = self.conditionTableWidget.rowCount()
        self.conditionTableWidget.insertRow(rowNumber)
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['logic'], LogicWidget())
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['name'], NameWidget())
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['comp'], CompWidget())
        self.conditionTableWidget.setItem(rowNumber, self.conditionRow['value'], QTableWidgetItem(""))

    def removeRowFromConditionTableWidget(self):
        self.conditionTableWidget.removeRow(self.conditionTableWidget.currentRow())

    def tableManagePushButtonClickedSlot(self):
        self.tableManagePushButton.setChecked(True)
        self.tableGeneratePushButton.setChecked(False)
        self.tableViewPushButton.setChecked(False)
        self.stackedWidget.setCurrentIndex(0)

    def tableGeneratePushButtonClickedSlot(self):
        self.tableManagePushButton.setChecked(False)
        self.tableGeneratePushButton.setChecked(True)
        self.tableViewPushButton.setChecked(False)
        self.stackedWidget.setCurrentIndex(1)

    def tableViewPushButtonClickedSlot(self):
        self.tableManagePushButton.setChecked(False)
        self.tableGeneratePushButton.setChecked(False)
        self.tableViewPushButton.setChecked(True)
        self.stackedWidget.setCurrentIndex(2)

    def condTableGenPushButtonClickedSlot(self):
        condition = ""
        for i in range(self.conditionTableWidget.rowCount()):
            if i >= 1:
                condition += " and "
            name = self.conditionTableWidget.cellWidget(i, self.conditionRow['name']).currentText()
            value = self.conditionTableWidget.item(i, self.conditionRow['value']).text()
            condition += self.conditionTableWidget.cellWidget(i, self.conditionRow['comp']).getCondition(name, value)
        self.addTabSignal.emit(condition)

    def importPushButtonClickedSlot(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "文件选择", os.getcwd(), "Excel Files (*.xls *.xlsx)")
        if filePath == '':  # 取消导出
            return
        filePath = filePath.replace('/', '\\')  # Excel不识别C:/xxx/xxx.xlsx的路径，只识别C:\xxx\xxx.xlsx
        print(filePath)
        excel = Easyexcel(filePath, visible=False)
        if SheetSelector(excel.get_sheet_names()).exec() == QDialog.Accepted:
            print("ok")
        else:
            print("cancel")
        excel.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = ManageWidget()
    myShow.show()
    sys.exit(app.exec_())
