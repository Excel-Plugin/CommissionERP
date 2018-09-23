import sys

from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QApplication, QHeaderView, \
    QTableView, QAbstractItemView, QComboBox, QTableWidgetItem
from PyQt5.uic import loadUi
import resources


class LogicWidget(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems(["并且", "或者"])


class CompWidget(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems(["等于", "不等于", "大于", "大于或等于", "小于", "小于或等于", "包含", "不包含", "为空值", "不为空值"])


class ManageWidget(QWidget):

    def __init__(self):
        super(ManageWidget, self).__init__()
        loadUi('manage_widget.ui', self)
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.tableManagePushButton.setChecked(True)
        self.tableManagePushButton.clicked.connect(self.tableManagePushButtonClickedSlot)
        self.tableGeneratePushButton.setChecked(False)
        self.tableGeneratePushButton.clicked.connect(self.tableGeneratePushButtonClickedSlot)
        self.tableViewPushButton.setChecked(False)
        self.tableViewPushButton.clicked.connect(self.tableViewPushButtonClickedSlot)
        # 业务表管理page0
        self.listTableWidget.horizontalHeader().setDefaultAlignment(Qt.Qt.AlignLeft)
        self.listTableWidget.horizontalHeader().setDefaultSectionSize(250)
        self.listTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 序时簿查看page2
        self.stackedWidget.setCurrentIndex(2)
        self.conditionTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # rowNumber = self.conditionTableWidget.rowCount()
        # self.conditionTableWidget.insertRow(rowNumber)
        # self.conditionTableWidget.setCellWidget(0, 0, LogicWidget())
        self.conditionTableWidget.removeRow(0)
        self.addRowToConditionTableWidget()
        self.addRowToConditionTableWidget()
        self.addRowToConditionTableWidget()

    def addRowToConditionTableWidget(self):
        rowNumber = self.conditionTableWidget.rowCount()
        print(rowNumber)
        self.conditionTableWidget.insertRow(rowNumber)
        self.conditionTableWidget.setCellWidget(rowNumber, 0, LogicWidget())
        self.conditionTableWidget.setItem(rowNumber, 2, QTableWidgetItem(""))
        self.conditionTableWidget.setCellWidget(rowNumber, 3, CompWidget())


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = ManageWidget()
    myShow.show()
    sys.exit(app.exec_())
