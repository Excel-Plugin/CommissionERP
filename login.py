import logging
import sys

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QStyleOption, QStyle, QLineEdit, QDialog, QMessageBox
from PyQt5 import QtGui
from PyQt5.uic import loadUi

from table_editor import TableEditor
import resources
from manage_widget import ManageWidget


class Login(QDialog):

    def __init__(self):
        super(QWidget, self).__init__()
        loadUi('login.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去掉标题栏
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)  # 密码输入
        self.loginPushButton.setCursor(QCursor(Qt.PointingHandCursor))  # 鼠标显示为手形
        self.exitPushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.exitPushButton.clicked.connect(sys.exit)
        self.loginPushButton.clicked.connect(self.login)

        self.__bPressFlag = False
        self.__beginDrag: QPoint = QPoint(0, 0)

    def login(self):
        if self.usernameLineEdit.text() == 'root' and self.passwordLineEdit.text() == '123456':
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")

    # 重写paintEvent，否则不能使用QSS样式表定义外观
    def paintEvent(self, a0: QtGui.QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 反锯齿
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        self.__bPressFlag = True
        self.__beginDrag = a0.pos()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        self.__bPressFlag = False

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent):
        if self.__bPressFlag:
            rel: QPoint = QPoint(QCursor.pos().x() - self.__beginDrag.x(), QCursor.pos().y() - self.__beginDrag.y())
            self.move(rel)


if __name__ == '__main__':
    logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s : %(levelname)s : %(message)s')
    logging.debug("程序开始启动...")
    try:
        app = QApplication(sys.argv)
        if Login().exec_() == QDialog.Accepted:
            logging.info("登录成功，正在初始化TableEditor")
            tableEditor = TableEditor()
            logging.info("TableEditor初始化完成，正在初始化ManageWidget")
            manageWidget = ManageWidget(tableEditor.addTabSignal)
            logging.info("ManageWidget初始化完成，正在调用show函数")
            manageWidget.show()
            sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.warning(None, "Exception", str(e))
        logging.exception(e)
