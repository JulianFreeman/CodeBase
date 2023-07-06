# code: utf8

#
# 创建翻译文件的办法：
# pyside6-lupdate myapp.py -ts myapp_zh_cn.ts
# 使用 Qt Linguist 打开 myapp_zh_cn.ts 翻译好之后，点击 文件-发布 生成 myapp_zh_cn.qm
# 将 .qm 文件包含在资源文件 myapp.qrc 中，该文件使用 Qt Designer 创建
# pyside6-rcc myapp.qrc -o myapp_rc.py
# 资源文件转换为 .py 文件后 import 进来，就可以使用了
#

import sys
import datetime
from PySide6 import QtWidgets, QtCore, QtGui

import myapp_rc


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(640, 360)
        window.setWindowIcon(QtGui.QIcon(":/myapp.ico"))

        self.vly_m = QtWidgets.QVBoxLayout()
        self.txe_top = QtWidgets.QTextEdit(window)
        self.txe_top.setReadOnly(True)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.txe_bot = QtWidgets.QTextEdit(window)

        self.vly_but = QtWidgets.QVBoxLayout()
        self.pbn_send = QtWidgets.QPushButton(window)
        self.pbn_clear = QtWidgets.QPushButton(window)

        self.cmbx_lang = QtWidgets.QComboBox(window)
        # self.cmbx_lang.addItems(["English", "中文", "日本語"])

        self.vly_but.addWidget(self.pbn_send)
        self.vly_but.addWidget(self.pbn_clear)
        self.vly_but.addWidget(self.cmbx_lang)

        self.hly_bot.addWidget(self.txe_bot)
        self.hly_bot.addLayout(self.vly_but)

        self.vly_m.addWidget(self.txe_top)
        self.vly_m.addLayout(self.hly_bot)
        self.txe_bot.setMaximumHeight(self.pbn_send.height() + self.pbn_clear.height() + self.cmbx_lang.height())

        window.setLayout(self.vly_m)

        self.re_translate_lock = False
        self.re_translate(window, 0)

    def re_translate(self, window: QtWidgets.QWidget, index: int):
        self.re_translate_lock = True

        window.setWindowTitle(QtCore.QCoreApplication.translate("MainWin", "My App"))
        self.txe_bot.setPlaceholderText(QtCore.QCoreApplication.translate("MainWin", "Enter something..."))
        self.pbn_send.setText(QtCore.QCoreApplication.translate("MainWin", "Send"))
        self.pbn_clear.setText(QtCore.QCoreApplication.translate("MainWin", "Clear"))

        self.cmbx_lang.clear()
        self.cmbx_lang.addItems([
            QtCore.QCoreApplication.translate("MainWin", "English"),
            QtCore.QCoreApplication.translate("MainWin", "Chinese"),
            QtCore.QCoreApplication.translate("MainWin", "Japanese"),
        ])
        self.cmbx_lang.setCurrentIndex(index)

        self.re_translate_lock = False


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)
        self.current_tr = None  # type: QtCore.QTranslator | None

        self.tr_zh_cn = QtCore.QTranslator()
        self.tr_zh_cn.load(":/translations/myapp_zh_cn.qm")
        self.tr_jp = QtCore.QTranslator()
        self.tr_jp.load(":/translations/myapp_jp.qm")

        self.ui.pbn_send.clicked.connect(self.on_pbn_send_clicked)
        self.ui.pbn_clear.clicked.connect(self.on_pbn_clear_clicked)
        self.ui.cmbx_lang.currentIndexChanged.connect(self.on_cmbx_lang_current_index_changed)

    def on_pbn_send_clicked(self):
        text = self.ui.txe_bot.toPlainText()
        if len(text) == 0:
            return
        else:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text = f"<{time}>\n{text}"

        origin = self.ui.txe_top.toPlainText()
        if len(origin) == 0:
            self.ui.txe_top.setPlainText(text)
        else:
            self.ui.txe_top.setPlainText(f"{origin}\n\n{text}")

        self.ui.txe_bot.clear()

    def on_pbn_clear_clicked(self):
        self.ui.txe_top.clear()

    def on_cmbx_lang_current_index_changed(self, index: int):
        if self.ui.re_translate_lock:
            return

        if self.current_tr is not None:
            QtCore.QCoreApplication.removeTranslator(self.current_tr)

        if index == 1:
            self.current_tr = self.tr_zh_cn
        elif index == 2:
            self.current_tr = self.tr_jp
        else:
            self.current_tr = None

        if self.current_tr is not None:
            QtCore.QCoreApplication.installTranslator(self.current_tr)

        self.ui.re_translate(self, index)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
