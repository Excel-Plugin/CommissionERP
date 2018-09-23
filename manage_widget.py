import sys

from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.uic import loadUi


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
        self.resultListWidget.addItem(QListWidgetItem("数据源表2018-08"))
        self.resultListWidget.addItem(QListWidgetItem("数据源表2018-07"))
        self.resultListWidget.addItem(QListWidgetItem("数据源表2018-06"))
        self.resultListWidget.addItem(QListWidgetItem("数据源表2018-05"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myShow = ManageWidget()
    myShow.show()
    sys.exit(app.exec_())
