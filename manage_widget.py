import os
import sys
import threading
import traceback
import time

import pythoncom
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QHeaderView, \
    QAbstractItemView, QComboBox, QTableWidgetItem, QFileDialog, QDialog, QMessageBox, QProgressDialog
from PyQt5.uic import loadUi
import resources  # 生成exe时需要此文件
from InterfaceModule import Easyexcel
from data_manager import DataManager
from excel_access import ExcelAccess
from sheet_selector import SheetSelector


class LogicComboBox(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems(["并且", "或者"])


class NameComboBox(QComboBox):

    def __init__(self, columns):
        super(QComboBox, self).__init__()
        self.addItems([c[1] for c in columns])


class CompComboBox(QComboBox):

    def __init__(self):
        super(QComboBox, self).__init__()
        self.addItems(["等于", "不等于", "大于", "大于或等于", "小于", "小于或等于", "包含", "不包含", "为空值", "不为空值"])

    def getCondition(self, column_types: dict, name: str, value: str):
        """根据当前选择返回SQL条件语句
        column_types：列名->列数据类型"""
        if 'text' in column_types[name]:  # 注意：若使用了其他的文本数据类型，这里需要更改
            value = "'" + value + "'"
        conditionDict = {"等于": name + " = " + value, "不等于": name + " != " + value,
                         "大于": name + " > " + value, "大于或等于": name + " >= " + value,
                         "小于": name + " < " + value, "小于或等于": name + " <= " + value,
                         # 注意：若关系为“包含”，则name必定为字符串相关类型，则value必定会两侧加''，所以下面需要去掉
                         "包含": name + " like '%" + value[1:-1] + "%' ",
                         "不包含": name + "not like '%" + value[1:-1] + "%' ",
                         "为空值": name + " is null ", "不为空值": name + " is not null "
                         }
        return conditionDict[self.currentText()]


# TODO: 把生成表格改为查看表格
class ManageWidget(QWidget):
    conditionRow = {'logic': 0, 'name': 2, 'comp': 3, 'value': 4}

    def __init__(self, addTabSignal):
        super(ManageWidget, self).__init__()
        loadUi('manage_widget.ui', self)
        # 数据库管理
        self.__dm = DataManager()
        # 整体界面设置
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
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['logic'], LogicComboBox())
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['name'],
                                                NameComboBox(self.__dm.get_columns('salesman')))  # TODO:这里需要改成要查看的序时簿
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['comp'], CompComboBox())
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
            condition += self.conditionTableWidget.cellWidget(i, self.conditionRow['comp']) \
                .getCondition(self.__dm.get_column_types('salesman'), name, value)  # TODO: 这里表名应为要查看序时簿的表名
        self.addTabSignal.emit(condition)

    progressSignal = QtCore.pyqtSignal(object)  # 进度框相关信息，注意参数只有一个object
    errorSignal = QtCore.pyqtSignal(object)  # 子线程错误信息

    def importPushButtonClickedSlot(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "文件选择", os.getcwd(), "Excel Files (*.xls *.xlsx)")
        if filePath == '':  # 取消导出
            return
        filePath = filePath.replace('/', '\\')  # Excel不识别C:/xxx/xxx.xlsx的路径，只识别C:\xxx\xxx.xlsx
        print(filePath)
        access = ExcelAccess()
        if access.exec() != QDialog.Accepted:
            return
        openPassword, editPassword = access.get_passwords()  # 获取用户输入的密码
        try:
            excel = Easyexcel(filePath, visible=False, access_password=openPassword, write_res_password=editPassword)
            selector = SheetSelector(excel.get_sheet_names(), self.__dm.get_my_tables('all'))
            excel.close()
            if selector.exec() == QDialog.Accepted:
                sheet_info = selector.get_sheet_info()  # sheet_info格式为[(Sheet名, 数据表类型, 数据表名称)]
                progressDlg = QProgressDialog("正在导入数据表", "Cancel", 0, len(sheet_info), self)
                progressDlg.setWindowTitle("正在导入")  # TODO: 对取消的处理
                progressDlg.setAutoClose(True)
                progressDlg.show()

                def slot(info):
                    progress, sheet_name, sheet_len = info
                    progressDlg.setValue(progress)
                    progressDlg.setLabelText(f"正在导入工作簿'{sheet_name}'({progress}/{sheet_len})")
                    if progress == progressDlg.maximum():
                        QMessageBox.information(self, "数据表导入成功", f"数据表'{filePath}'已成功导入")

                self.progressSignal.connect(slot)

                def error_slot(err):
                    QMessageBox.warning(self, "导入出错", str(err))

                self.errorSignal.connect(error_slot)

                def process():
                    try:
                        pythoncom.CoInitialize()
                        ex = Easyexcel(filePath, visible=False, access_password=openPassword,
                                       write_res_password=editPassword)
                        dm = DataManager()  # 子线程要创建一个单独的数据管理类
                        for i, sheet in enumerate(sheet_info):  # sheet_info格式为[(Sheet名, 数据表类型, 数据表名称)]
                            sheet_name, table_type, table_name = sheet
                            header_dict, sheet_data = ex.get_sheet(sheet_name)
                            dm.create_table(table_type, table_name, list(header_dict.keys()))
                            # 此处将表头按照顺序排列。如果header_dict和sheet_data不匹配的话可能会出问题
                            dm.insert_data(table_name, sorted(header_dict.keys(), key=lambda x: header_dict[x]),
                                           sheet_data)
                            self.progressSignal.emit((i + 1, sheet_name, len(sheet_info)))
                            self.progressSignal.emit((i + 1, "test", len(sheet_info)))
                    except Exception as err:
                        traceback.print_exc(err)
                        self.errorSignal.emit(err)

                threading.Thread(target=process, daemon=True).start()
            else:
                print("cancel")
        except Exception as e:
            QMessageBox.warning(self, str(e), traceback.format_exc())

