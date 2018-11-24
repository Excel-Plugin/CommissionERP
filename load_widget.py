from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.uic import loadUi


class LoadWidget(QWidget):

    def __init__(self, parent):
        super(LoadWidget, self).__init__(parent=parent)
        loadUi("load_widget.ui", self)
        self.setWindowModality(Qt.ApplicationModal)  # 阻塞此应用的窗口
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 去掉边框之后导致不能阻塞了，所以要加上Qt.Dialog
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        movie = QMovie("img/loading.gif")
        self.label.setMovie(movie)
        movie.start()
