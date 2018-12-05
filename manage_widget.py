import logging
import os
import threading

import pythoncom
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QMetaMethod
from PyQt5.QtWidgets import QWidget, QApplication, QHeaderView, \
    QAbstractItemView, QComboBox, QTableWidgetItem, QFileDialog, QDialog, QMessageBox, QProgressDialog, QSizePolicy, \
    QListWidgetItem
from PyQt5.uic import loadUi
import resources  # 生成exe时需要此文件
from InterfaceModule import Easyexcel
from data_manager import DataManager
from excel_access import ExcelAccess
from excel_check import ExcelCheck
from load_widget import LoadWidget
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


# TODO: 把生成表格改为查看表格，再加一个删除表格
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
        items = [QListWidgetItem(n) for n in ExcelCheck.headers.keys()]  # 注意："全部表格"直接放在UI里面了
        for item in items:
            item.setTextAlignment(Qt.AlignCenter)
            self.selectListWidget.addItem(item)
        self.selectListWidget.setCurrentRow(0)
        self.selectListWidget.currentItemChanged.connect(self.changeListTableSlot)
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

    def changeListTableSlot(self):
        """左侧所选表格类型改变后会触发此函数，用于更新右侧表格listTableWidget列表内容"""
        print(f"change to {self.selectListWidget.currentItem()}")

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

    loadingSignal = QtCore.pyqtSignal(object)  # 读取sheet的进度框，可能为True表示完成，也可能为Exception表示出错

    def importPushButtonClickedSlot(self):
        self.importPushButton.setEnabled(False)  # 处理期间不能点击
        filePath, _ = QFileDialog.getOpenFileName(self, "文件选择", os.getcwd(), "Excel Files (*.xls *.xlsx)")
        if filePath == '':  # 取消导出
            self.importPushButton.setEnabled(True)
            return
        filePath = filePath.replace('/', '\\')  # Excel不识别C:/xxx/xxx.xlsx的路径，只识别C:\xxx\xxx.xlsx
        print(filePath)
        access = ExcelAccess()
        if access.exec() != QDialog.Accepted:
            self.importPushButton.setEnabled(True)
            return
        openPassword, editPassword = access.get_passwords()  # 获取用户输入的密码
        try:
            # 显示正在加载中
            loadWgt = LoadWidget(parent=self)
            loadWgt.show()

            try:
                self.loadingSignal.disconnect()  # 断开与self.loadingSignal所关联的所有槽（主要是断开以前关联过的槽函数）
            except Exception:
                pass  # 在第一次disconnect时，由于没有与self.loadingSignal关联的槽，会抛出异常，这是正常情况，什么也不需要做

            def loading_slot(info):
                if isinstance(info, list):
                    if info:
                        try:
                            print("get signal:"+str(info))
                            loadWgt.close()
                            selector = SheetSelector(info, self.__dm.get_tables())
                            # 导入数据表
                            if selector.exec() == QDialog.Accepted:
                                sheet_info = selector.get_sheet_info()  # sheet_info格式为[(Sheet名, 数据表类型, 数据表名称)]
                                if len(sheet_info) > 0:  # 若没有要导入的，则为空（这里不要直接返回，此函数结尾要恢复按钮状态）
                                    self.importSheetsToDb(filePath, openPassword, editPassword, sheet_info)
                                    return  # 这里由于非阻塞，所以线程尚未完成就会返回，此时按钮应该仍为不可点击状态，应子线程完成的槽函数内恢复状态
                        except Exception as e:
                            QMessageBox.warning(self, "导入出错", str(e))
                            logging.exception(e)
                elif isinstance(info, Exception):
                    QMessageBox.warning(self, "读取出错", str(info))
                    loadWgt.close()
                self.importPushButton.setEnabled(True)  # 处理结束之后恢复可以点击的状态

            self.loadingSignal.connect(loading_slot)

            def loading_work():
                try:
                    # 读取数据表的sheet信息
                    pythoncom.CoInitialize()
                    excel = Easyexcel(filePath, visible=False, access_password=openPassword, write_res_password=editPassword)
                    sheet_names = excel.get_sheet_names()
                    excel.close()
                    self.loadingSignal.emit(sheet_names)
                except Exception as e:
                    logging.exception(e)
                    self.loadingSignal.emit(e)

            threading.Thread(target=loading_work, daemon=True).start()
        except Exception as exp:
            QMessageBox.warning(self, "导入出错", str(exp))

    # 如下两个信号只与importSheetsToDb有关
    progressSignal = QtCore.pyqtSignal((int, str))  # 进度框相关信息，注意参数只有一个object
    errorSignal = QtCore.pyqtSignal(object)  # 子线程错误信息

    def importSheetsToDb(self, filePath, openPassword, editPassword, sheet_info):
        progressDlg = QProgressDialog("正在读取数据表", "Cancel", 0, len(sheet_info), self)
        progressDlg.setWindowTitle("正在导入")  # 注意：这里即使关闭窗口，导入过程仍然会正常进行
        progressDlg.setAutoClose(True)
        progressDlg.setWindowModality(Qt.ApplicationModal)
        progressDlg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        progressDlg.setStyleSheet("""QDialog{ border: 1px solid rgb(85,85,85); } 
        QProgressBar{border: 2px solid grey; border-radius: 5px; color: black; text-align: center;}""")
        progressDlg.setCancelButton(None)
        progressDlg.show()

        def slot(value, text):
            progressDlg.setValue(value)
            progressDlg.setLabelText(text)
            if value == progressDlg.maximum():
                QMessageBox.information(self, "数据表导入成功", f"数据表'{filePath}'已成功导入")
                self.importPushButton.setEnabled(True)

        self.progressSignal.connect(slot)

        def error_slot(err):
            progressDlg.close()
            self.importPushButton.setEnabled(True)
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
                    self.progressSignal.emit(i, f"正在导入工作簿'{sheet_name}'({i}/{len(sheet_info)})")
                    header_dict, sheet_data = ex.get_sheet(sheet_name)
                    flag, msg = ExcelCheck.characters_check(sheet_data)
                    if not flag:
                        ex.close()
                        raise Exception(msg)
                    if table_type == '售后员提成明细':
                        sheet_data = ExcelCheck.formatted_after_sales(header_dict, sheet_data)
                        dm.create_table(table_type, table_name, ExcelCheck.headers["售后员提成明细"])
                        dm.insert_data(table_name, ExcelCheck.headers["售后员提成明细"], sheet_data)
                    else:
                        # 过滤掉列名中的特殊字符以防导致SQL命令格式错误
                        f_header_dict = {k.replace('\n', ''): v for k, v in header_dict.items()}
                        columns = sorted(f_header_dict.keys(), key=lambda x: f_header_dict[x])  # 与Excel表格列顺序相同
                        dm.create_table(table_type, table_name, columns)
                        # 此处将表头按照顺序排列。如果header_dict和sheet_data不匹配的话可能会出问题
                        dm.insert_data(table_name, columns, sheet_data)
                ex.close()
                self.progressSignal.emit(len(sheet_info), "导入完成")

            except Exception as err:
                logging.exception(err)
                self.errorSignal.emit(err)

        threading.Thread(target=process, daemon=True).start()

