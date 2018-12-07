import logging
import os
import threading
import time

import pythoncom
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication, QHeaderView, \
    QAbstractItemView, QComboBox, QTableWidgetItem, QFileDialog, QDialog, QMessageBox, QProgressDialog, QSizePolicy, \
    QListWidgetItem, QPushButton
from PyQt5.uic import loadUi
import resources  # 生成exe时需要此文件
from CalcRatio import CalcRatio
from InterfaceModule import Easyexcel
from after_sales import AfterSales
from bonus import Bonus
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
        self.addItems(columns)


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


class TableNamePushButton(QPushButton):
    doubleClickSignal = pyqtSignal(object)  # 这里传的是一个元组(表名, 条件)

    def __init__(self, name):
        super(TableNamePushButton, self).__init__(name)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent):
        self.doubleClickSignal.emit(self.text())


class ManageWidget(QWidget):
    conditionRow = {'logic': 0, 'name': 2, 'comp': 3, 'value': 4}

    def __init__(self, addTabSignal):
        super(ManageWidget, self).__init__()
        loadUi('manage_widget.ui', self)
        # 数据库管理
        self.__dm = DataManager()
        # 整体界面初始化
        self.addTabSignal = addTabSignal
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.tableManagePushButton.setChecked(True)
        self.tableManagePushButton.clicked.connect(self.tableManagePushButtonClickedSlot)
        self.tableGeneratePushButton.setChecked(False)
        self.tableGeneratePushButton.clicked.connect(self.tableGeneratePushButtonClickedSlot)
        self.tableViewPushButton.setChecked(False)
        self.tableViewPushButton.clicked.connect(self.tableViewPushButtonClickedSlot)
        self.stackedWidget.currentChanged.connect(self.currentChangedSlot)
        # 业务表管理page0
        # 表格类型选择初始化为"全部表格"
        items = [QListWidgetItem(n) for n in ExcelCheck.headers.keys()]  # 注意："全部表格"直接放在UI里面了
        for item in items:
            item.setTextAlignment(Qt.AlignCenter)
            self.selectListWidget.addItem(item)
        self.selectListWidget.currentItemChanged.connect(self.changeListTableSlot)
        self.selectListWidget.setCurrentRow(0)  # 设置选中项放在connect之后，这样就会调用changeListTableSlot来初始化右侧表格
        self.importPushButton.clicked.connect(self.importPushButtonClickedSlot)
        self.generatePushButton.clicked.connect(self.tableGeneratePushButtonClickedSlot)  # 生成表格的按钮与切换业务表生成效果完全相同
        self.removePushButton.clicked.connect(self.removePushButtonClickedSlot)
        self.searchPushButton.clicked.connect(self.searchPushButtonClickedSlot)
        # 表格列表初始化为全部表格的列表
        self.listTableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.listTableWidget.horizontalHeader().setDefaultSectionSize(250)
        self.listTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 业务表生成page1
        self.cmsTableGenPushButton.clicked.connect(self.cmsTableGenPushButtonClickedSlot)
        self.genProgressBar.setRange(0, 100)
        self.genProgressBar.setValue(0)
        # 序时簿查看page2
        self.conditionTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.conditionTableWidget.removeRow(0)
        self.addConditionPushButton.clicked.connect(self.addRowToConditionTableWidget)
        self.deleteConditionPushButton.clicked.connect(self.removeRowFromConditionTableWidget)
        self.condTableGenPushButton.clicked.connect(self.condTableGenPushButtonClickedSlot)
        # 各页面初始化好以后，进行整体界面设置
        self.stackedWidget.setCurrentIndex(0)

    def currentChangedSlot(self, index):
        """槽函数：用户所选widget改变"""
        if index == 0:
            # 当用户切换到业务表管理的页面时，更新当前显示的表单
            self.changeListTableSlot()
        elif index == 1:
            # 当用户切换到了业务表生成的页面，更新ComboBox
            self.dataSourceComboBox.addItems(self.__dm.get_my_tables("数据源表"))
            self.ruleComboBox.addItems(self.__dm.get_my_tables("规则表"))
            self.priceComboBox.addItems(self.__dm.get_my_tables("指导价表"))
            self.clientComboBox.addItems(self.__dm.get_my_tables("客户编号表"))
            self.managerComboBox.addItems(self.__dm.get_my_tables("主管表"))
            self.aftersalesComboBox.addItems(self.__dm.get_my_tables("售后员表"))

    def changeListTableSlot(self):
        """槽函数：左侧所选表格类型改变后会触发此函数，用于更新右侧表格listTableWidget列表内容"""
        for i in reversed(range(self.listTableWidget.rowCount())):  # 清空表格
            self.listTableWidget.removeRow(i)
        info_list = self.__dm.get_my_tables_info(self.selectListWidget.currentItem().text())
        for table_info in info_list:
            table_name, table_type, create_time = table_info  # 每个元素为一个元组(表名,类型,秒级时间戳)
            rowNumber = self.listTableWidget.rowCount()
            self.listTableWidget.insertRow(rowNumber)
            nameItem = TableNamePushButton(table_name)
            nameItem.doubleClickSignal.connect(self.tableNameDoubleClickedSlot)
            self.listTableWidget.setCellWidget(rowNumber, 0, nameItem)
            typeItem = QTableWidgetItem(table_type)
            typeItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            typeItem.setFlags(typeItem.flags() & ~Qt.ItemIsEditable)  # 设置不可修改
            self.listTableWidget.setItem(rowNumber, 1, typeItem)
            timeItem = QTableWidgetItem(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time)))
            timeItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            timeItem.setFlags(timeItem.flags() & ~Qt.ItemIsEditable)  # 设置不可修改
            self.listTableWidget.setItem(rowNumber, 2, timeItem)

    def removePushButtonClickedSlot(self):
        """槽函数：业务表管理>删除表格"""
        if len(self.listTableWidget.selectedRanges()) <= 0:
            QMessageBox.warning(self, "无法删除", "尚未选中要删除的表格")
            return
        try:
            # 删除时要按照最小索引从大往小删除
            for selection in sorted(self.listTableWidget.selectedRanges(), key=lambda x: x.topRow(), reverse=True):
                top, bottom = selection.topRow(), selection.bottomRow()
                for i in reversed(range(top, bottom+1)):  # 删除列表时要按照索引从大往小删除
                    self.__dm.remove_table(self.listTableWidget.cellWidget(i, 0).text())
                    self.listTableWidget.removeRow(i)
        except Exception as e:
            logging.exception(e)
            QMessageBox.warning(self, "删除失败", str(e))

    def searchPushButtonClickedSlot(self):
        """槽函数：业务表管理>点击搜索"""
        for i in reversed(range(self.listTableWidget.rowCount())):  # 清空表格
            self.listTableWidget.removeRow(i)
        info_list = self.__dm.get_my_tables_info(self.selectListWidget.currentItem().text())
        for table_info in info_list:
            table_name, table_type, create_time = table_info  # 每个元素为一个元组(表名,类型,秒级时间戳)
            if self.searchLineEdit.text() in table_name:  # 将符合条件的表格显示出来
                rowNumber = self.listTableWidget.rowCount()
                self.listTableWidget.insertRow(rowNumber)
                nameItem = TableNamePushButton(table_name)
                nameItem.doubleClickSignal.connect(self.tableNameDoubleClickedSlot)
                self.listTableWidget.setCellWidget(rowNumber, 0, nameItem)
                typeItem = QTableWidgetItem(table_type)
                typeItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                typeItem.setFlags(typeItem.flags() & ~Qt.ItemIsEditable)  # 设置不可修改
                self.listTableWidget.setItem(rowNumber, 1, typeItem)
                timeItem = QTableWidgetItem(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time)))
                timeItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                timeItem.setFlags(timeItem.flags() & ~Qt.ItemIsEditable)  # 设置不可修改
                self.listTableWidget.setItem(rowNumber, 2, timeItem)

    def tableNameDoubleClickedSlot(self, name):
        """槽函数：双击表格名称，打开表格查看"""
        self.addTabSignal.emit((name, "", False))

    generateCmsSignal = pyqtSignal(object)  # 生成提成表单子线程的信号

    def cmsTableGenPushButtonClickedSlot(self):
        """槽函数：点击生成提成表单按钮"""
        if self.cmsLineEdit.text() == '' and self.asCmsLineEdit.text() == '':
            QMessageBox.warning(self, "无法生成", "业务员提成明细和售后员提成明细均为空，请填写要生成的表单名称")
            return
        table_names = self.__dm.get_tables()
        if self.cmsLineEdit.text() in table_names:
            QMessageBox.warning(self, "无法生成", f"表格'{self.cmsLineEdit.text()}'已存在")
            return
        if self.asCmsLineEdit.text() in table_names:
            QMessageBox.warning(self, "无法生成", f"表格'{self.asCmsLineEdit.text()}'已存在")
            return

        def generateCmsSlot(info):
            if isinstance(info, str):  # info为生成完成的表格
                QMessageBox.information(self, "表单已生成", f'{info}已生成，请在业务表管理页面查看')
            elif isinstance(info, Exception):  # 出现异常
                self.cmsTableGenPushButton.setEnabled(True)
                logging.exception(info)
                QMessageBox.warning(self, "生成出错", str(info))

        self.generateCmsSignal.connect(generateCmsSlot)
        threading.Thread(target=self.generateCmsTableWork, daemon=True).start()
        self.cmsTableGenPushButton.setEnabled(False)
        QMessageBox.information(self, "正在生成表单", "正在生成表单，期间请不要查看其它页面")

    def generateCmsTableWork(self):
        """子线程函数：生成提成表单并写入数据库"""
        try:
            dm = DataManager()
            src_dict, src_data = dm.get_table(self.dataSourceComboBox.currentText())
            rul_dict, rul_data = dm.get_table(self.ruleComboBox.currentText())
            calc_ratio = CalcRatio(rul_dict, rul_data)
            clt_dict, clt_data = dm.get_table(self.clientComboBox.currentText())
            client_dict = {}  # 映射关系：客户编号->该客户对应行
            for row in clt_data:
                client_dict[row[clt_dict['客户编号']]] = row
            sht2_head, sht2 = dm.get_table(self.priceComboBox.currentText())
            price = []
            for row in sht2:
                price.append(
                    [row[sht2_head['编号']], row[sht2_head['指导单价(未税)\n元/KG']], row[sht2_head['备注']], row[sht2_head['出货开始时间']],
                     row[sht2_head['出货结束时间']]])
            sht4_head, sht4 = dm.get_table(self.managerComboBox.currentText())
            slr_dict, slr_data = dm.get_table(self.aftersalesComboBox.currentText())
            places = []  # 售后员表中的地点名
            for row in slr_data:
                if row[1] != 'None':
                    places.append([row[1], row[5], row[6]])
            self.genProgressBar.setValue(10)

            # 每次增加的进度=剩余进度(90)/每个表的阶段数(3)/要生成的表数
            piece = 30/len([x for x in [self.cmsLineEdit.text(), self.asCmsLineEdit.text()] if x != ''])
            if self.cmsLineEdit.text() != '':
                bs = Bonus(price)
                h1, r1, r2 = bs.calc_commission(src_dict, src_data, clt_dict, client_dict, rul_dict, rul_data, places, sht4)
                self.genProgressBar.setValue(self.genProgressBar.value()+piece)
                # 下面的h1应该是与ExcelCheck.headers["业务员提成明细"]完全相同的
                dm.create_table("业务员提成明细", self.cmsLineEdit.text(), h1)
                self.genProgressBar.setValue(self.genProgressBar.value() + piece)
                dm.insert_data(self.cmsLineEdit.text(), h1, r1)
                self.genProgressBar.setValue(self.genProgressBar.value() + piece)
                self.generateCmsSignal.emit(self.cmsLineEdit.text())
                self.cmsLineEdit.setText("")  # 清空表名
            if self.asCmsLineEdit.text() != '':
                after_sales = AfterSales(slr_dict, slr_data)
                as_header, as_content = after_sales.calc_commission(src_dict, src_data, clt_dict, client_dict, calc_ratio)
                self.genProgressBar.setValue(self.genProgressBar.value() + piece)
                # 下面的as_header应该是与ExcelCheck.headers["售后员提成明细"]完全相同的
                dm.create_table("售后员提成明细", self.asCmsLineEdit.text(), as_header)
                self.genProgressBar.setValue(self.genProgressBar.value() + piece)
                dm.insert_data(self.asCmsLineEdit.text(), as_header, as_content)
                self.genProgressBar.setValue(self.genProgressBar.value() + piece)
                self.generateCmsSignal.emit(self.asCmsLineEdit.text())
                self.asCmsLineEdit.setText("")  # 清空表名
            self.cmsTableGenPushButton.setEnabled(True)
        except Exception as e:
            logging.exception(e)
            QMessageBox.warning(self, "生成出错", str(e))

    def addRowToConditionTableWidget(self):
        rowNumber = self.conditionTableWidget.rowCount()
        self.conditionTableWidget.insertRow(rowNumber)
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['logic'], LogicComboBox())
        self.conditionTableWidget.setCellWidget(rowNumber, self.conditionRow['name'],
                                                NameComboBox(ExcelCheck.headers[self.tableTypeComboBox.currentText()]))
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
            # TODO: 虽然数据库中所有列都是text，但这里可能需要根据具体数据类型计算
            condition += self.conditionTableWidget.cellWidget(i, self.conditionRow['comp']) \
                .getCondition({x: 'text' for x in ExcelCheck.headers[self.tableTypeComboBox.currentText()]}, name, value)
        self.addTabSignal.emit((self.tableTypeComboBox.currentText(), condition, True))

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

