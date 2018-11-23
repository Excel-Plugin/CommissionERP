import sys

from PyQt5.QtWidgets import QDialog, QLineEdit, QApplication
from PyQt5.uic import loadUi


class ExcelAccess(QDialog):

    def __init__(self):
        super(ExcelAccess, self).__init__()
        loadUi('excel_access.ui', self)
        self.openPasswordLineEdit.setEchoMode(QLineEdit.Password)  # 密码输入
        self.editPasswordLineEdit.setEchoMode(QLineEdit.Password)  # 密码输入

    def get_passwords(self):
        return self.openPasswordLineEdit.text(), self.editPasswordLineEdit.text()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(ExcelAccess().exec())
    sys.exit(app.exec_())
