# code: utf8
import sys
from PySide6 import QtWidgets, QtCore, QtGui


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(640, 360)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.pte_1 = QtWidgets.QPlainTextEdit(window)
        # 设置为自定义菜单，则用户右击时会触发 customContextMenuRequested 信号
        self.pte_1.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.pte_2 = QtWidgets.QPlainTextEdit(window)
        self.vly_m.addWidget(self.pte_2)
        self.vly_m.addWidget(self.pte_1)

        self.act_cut = QtGui.QAction(window)
        self.act_copy = QtGui.QAction(window)
        self.act_paste = QtGui.QAction(window)

        self.menu_ctx = QtWidgets.QMenu(window)
        self.menu_ctx.addAction(self.act_cut)
        self.menu_ctx.addSeparator()
        self.menu_ctx.addAction(self.act_copy)
        self.menu_ctx.addAction(self.act_paste)

        window.setLayout(self.vly_m)

        self.re_translate_lock = False
        self.re_translate(window, 0)

    def re_translate(self, window: QtWidgets.QWidget, index: int):
        self.re_translate_lock = True

        window.setWindowTitle(QtCore.QCoreApplication.translate("MainWin", "Context Menu"))
        self.act_cut.setText(QtCore.QCoreApplication.translate("MainWin", "Cut"))
        self.act_copy.setText(QtCore.QCoreApplication.translate("MainWin", "Copy"))
        self.act_paste.setText(QtCore.QCoreApplication.translate("MainWin", "Paste"))

        self.re_translate_lock = False


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)

        # 将 customContextMenuRequested 信号绑定一个槽函数
        self.ui.pte_1.customContextMenuRequested.connect(self.on_pte_1_custom_context_menu_requested)
        self.ui.act_cut.triggered.connect(self.on_act_cut_triggered)

    def on_act_cut_triggered(self):
        self.ui.pte_1.appendPlainText("Cut")

    def on_pte_1_custom_context_menu_requested(self, pos: QtCore.QPoint):
        self.ui.act_copy.setEnabled(False)
        """
        This signal is emitted when the widget's contextMenuPolicy is Qt::CustomContextMenu, 
        and the user has requested a context menu on the widget. 
        The position pos is the position of the context menu event that the widget receives. 
        Normally this is in widget coordinates. 
        The exception to this rule is QAbstractScrollArea and its subclasses that map the context menu event 
        to coordinates of the viewport().
        """
        # QPlainTextEdit 属于 QAbstractScrollArea 的子类，需要调整位置
        self.ui.menu_ctx.exec(self.ui.pte_1.mapToGlobal(pos))
        # 右键菜单结束
        self.ui.act_copy.setEnabled(True)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        # 主窗口的右键菜单
        self.ui.menu_ctx.exec(event.globalPos())


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
