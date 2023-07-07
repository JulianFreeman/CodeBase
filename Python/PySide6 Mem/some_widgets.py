import sys
from PySide6 import QtWidgets, QtCore, QtGui


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(540, 360)
        window.setWindowTitle("Style")

        self.lb_style = QtWidgets.QLabel("Style: ", window)
        self.cmbx_style = QtWidgets.QComboBox(window)
        self.cmbx_style.addItem("Default")
        self.cbx_use_std = QtWidgets.QCheckBox("Use style's standard palette", window)
        self.cbx_disable_wg = QtWidgets.QCheckBox("Disable widgets", window)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.hly_top.addWidget(self.lb_style)
        self.hly_top.addWidget(self.cmbx_style)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.cbx_use_std)
        self.hly_top.addWidget(self.cbx_disable_wg)

        self.gbx_left = QtWidgets.QGroupBox("Group 1", window)
        self.rbn_1 = QtWidgets.QRadioButton("Radio button 1", self.gbx_left)
        self.rbn_2 = QtWidgets.QRadioButton("Radio button 2", self.gbx_left)
        self.rbn_3 = QtWidgets.QRadioButton("Radio button 3", self.gbx_left)
        self.cbx_tri = QtWidgets.QCheckBox("Tri-state check box", window)
        self.cbx_tri.setTristate(True)
        self.vly_gbx_left = QtWidgets.QVBoxLayout()
        self.vly_gbx_left.addWidget(self.rbn_1)
        self.vly_gbx_left.addWidget(self.rbn_2)
        self.vly_gbx_left.addWidget(self.rbn_3)
        self.vly_gbx_left.addWidget(self.cbx_tri)
        self.gbx_left.setLayout(self.vly_gbx_left)

        self.gbx_right = QtWidgets.QGroupBox("Group 2", window)
        self.pbn_1 = QtWidgets.QPushButton("Default push button", self.gbx_right)
        self.pbn_2 = QtWidgets.QPushButton("Toggle push button", self.gbx_right)
        self.pbn_3 = QtWidgets.QPushButton("Flat push button", self.gbx_right)
        self.pbn_2.setCheckable(True)
        self.pbn_2.setChecked(True)
        self.pbn_3.setFlat(True)
        self.vly_gbx_right = QtWidgets.QVBoxLayout()
        self.vly_gbx_right.addWidget(self.pbn_1)
        self.vly_gbx_right.addWidget(self.pbn_2)
        self.vly_gbx_right.addWidget(self.pbn_3)
        self.gbx_right.setLayout(self.vly_gbx_right)

        self.gbx_bot = QtWidgets.QGroupBox("Group 3", window)
        self.gbx_bot.setCheckable(True)
        self.gbx_bot.setChecked(False)
        self.lne_pswd = QtWidgets.QLineEdit("pass", self.gbx_bot)
        self.lne_pswd.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.sbx_1 = QtWidgets.QSpinBox(self.gbx_bot)
        self.sbx_1.setValue(50)
        self.dte_1 = QtWidgets.QDateTimeEdit(self.gbx_bot)
        self.dte_1.setDateTime(QtCore.QDateTime.currentDateTime())

        self.hsd_1 = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self.gbx_bot)
        self.hsb_1 = QtWidgets.QScrollBar(QtCore.Qt.Orientation.Horizontal, self.gbx_bot)
        self.dia_1 = QtWidgets.QDial(self.gbx_bot)
        self.gly_gbx_bot = QtWidgets.QGridLayout()
        self.gly_gbx_bot.addWidget(self.hsd_1, 0, 0)
        self.gly_gbx_bot.addWidget(self.hsb_1, 1, 0)
        self.gly_gbx_bot.addWidget(self.dia_1, 0, 1, 0, 1)
        self.vly_gbx_bot = QtWidgets.QVBoxLayout()
        self.vly_gbx_bot.addWidget(self.lne_pswd)
        self.vly_gbx_bot.addWidget(self.sbx_1)
        self.vly_gbx_bot.addWidget(self.dte_1)
        self.vly_gbx_bot.addLayout(self.gly_gbx_bot)
        self.gbx_bot.setLayout(self.vly_gbx_bot)

        self.tabw_1 = QtWidgets.QTabWidget(window)
        self.tbw_1 = QtWidgets.QTableWidget(5, 5, window)
        self.txe_1 = QtWidgets.QTextEdit(window)
        self.tabw_1.addTab(self.tbw_1, "Table")
        self.tabw_1.addTab(self.txe_1, "Text Edit")

        self.gly_mid = QtWidgets.QGridLayout()
        self.gly_mid.addWidget(self.gbx_left, 0, 0)
        self.gly_mid.addWidget(self.gbx_right, 0, 1)
        self.gly_mid.addWidget(self.tabw_1, 1, 0)
        self.gly_mid.addWidget(self.gbx_bot, 1, 1)
        self.gly_mid.setRowStretch(0, 1)
        self.gly_mid.setRowStretch(1, 1)
        self.gly_mid.setColumnStretch(0, 1)
        self.gly_mid.setColumnStretch(1, 1)

        self.pgb_1 = QtWidgets.QProgressBar(window)
        self.pgb_1.setValue(15)
        self.pgb_1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.vly_m.addLayout(self.gly_mid)
        self.vly_m.addWidget(self.pgb_1)

        window.setLayout(self.vly_m)


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
