import sys

from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QApplication, QHeaderView
from PyQt5.uic import loadUi
import resources


class ListWidgetItem(QListWidgetItem):

    def __init__(self):
        super(ListWidgetItem, self).__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("数据源表2018-08"))
        layout.addWidget(QPushButton("打开"))
        layout.addWidget(QPushButton("删除"))
        self.setLayout(layout)


class ManageWidget(QWidget):

    def __init__(self):
        super(ManageWidget, self).__init__()
        loadUi('manage_widget.ui', self)
        self.setWindowFlags(Qt.Qt.WindowMinimizeButtonHint | Qt.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.listTableWidget.horizontalHeader().setDefaultAlignment(Qt.Qt.AlignLeft)
        self.listTableWidget.horizontalHeader().setDefaultSectionSize(250)
        self.tableManagePushButton.setChecked(True)
        self.tableManagePushButton.clicked.connect(self.tableManagePushButtonClickedSlot)
        self.tableGeneratePushButton.setChecked(False)
        self.tableGeneratePushButton.clicked.connect(self.tableGeneratePushButtonClickedSlot)
        self.tableViewPushButton.setChecked(False)
        self.tableViewPushButton.clicked.connect(self.tableViewPushButtonClickedSlot)

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
