# code: utf8
from PySide6 import QtWidgets, QtCore

from jnlib.pyside6_utils import PushButtonWithId, HorizontalLine


class ChromSettingsWin(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.resize(540, 140)
        self.setWindowTitle("设置")

        self.vly_m = QtWidgets.QVBoxLayout()
        self.gly_paths = QtWidgets.QGridLayout()

        self.lb_chrome = QtWidgets.QLabel("Chrome", self)
        self.lb_edge = QtWidgets.QLabel("Edge", self)
        self.lb_brave = QtWidgets.QLabel("Brave", self)
        self.lne_chrome = QtWidgets.QLineEdit(self)
        self.lne_edge = QtWidgets.QLineEdit(self)
        self.lne_brave = QtWidgets.QLineEdit(self)
        self.pbn_chrome = PushButtonWithId("Chrome", self, "选择")
        self.pbn_edge = PushButtonWithId("Edge", self, "选择")
        self.pbn_brave = PushButtonWithId("Brave", self, "选择")

        self.lb_plg_db = QtWidgets.QLabel("预存库", self)
        self.lne_plg_db = QtWidgets.QLineEdit(self)
        self.pbn_plg_db = PushButtonWithId("Plugin DB", self, "选择")

        self.gly_paths.addWidget(self.lb_chrome, 0, 0)
        self.gly_paths.addWidget(self.lb_edge, 1, 0)
        self.gly_paths.addWidget(self.lb_brave, 2, 0)
        self.gly_paths.addWidget(self.lne_chrome, 0, 1)
        self.gly_paths.addWidget(self.lne_edge, 1, 1)
        self.gly_paths.addWidget(self.lne_brave, 2, 1)
        self.gly_paths.addWidget(self.pbn_chrome, 0, 2)
        self.gly_paths.addWidget(self.pbn_edge, 1, 2)
        self.gly_paths.addWidget(self.pbn_brave, 2, 2)

        self.hln_1 = HorizontalLine(self)

        self.gly_paths.addWidget(self.hln_1, 3, 0, 1, 3)

        self.gly_paths.addWidget(self.lb_plg_db, 4, 0)
        self.gly_paths.addWidget(self.lne_plg_db, 4, 1)
        self.gly_paths.addWidget(self.pbn_plg_db, 4, 2)

        self.hln_2 = HorizontalLine(self)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_save = QtWidgets.QPushButton("保存", self)
        self.pbn_remove = QtWidgets.QPushButton("清除", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)

        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_save)
        self.hly_bot.addWidget(self.pbn_remove)
        self.hly_bot.addWidget(self.pbn_cancel)

        self.vly_m.addLayout(self.gly_paths)
        self.vly_m.addWidget(self.hln_2)
        self.vly_m.addLayout(self.hly_bot)
        self.vly_m.addStretch(1)
        self.setLayout(self.vly_m)

        self.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.pbn_remove.clicked.connect(self.on_pbn_remove_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)
        self.pbn_chrome.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)
        self.pbn_edge.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)
        self.pbn_brave.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)
        self.pbn_plg_db.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)

        self._read_settings()

    def _read_settings(self):
        us = QtCore.QSettings()
        chrome_exec = us.value("chrome_exec", "")  # type: str | object
        edge_exec = us.value("edge_exec", "")  # type: str | object
        brave_exec = us.value("brave_exec", "")  # type: str | object
        plg_db = us.value("plg_db", "")  # type: str | object
        self.lne_chrome.setText(chrome_exec)
        self.lne_edge.setText(edge_exec)
        self.lne_brave.setText(brave_exec)
        self.lne_plg_db.setText(plg_db)

    def on_pbn_n_clicked_with_id(self, ids: str):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, f"选择 {ids}")
        if len(filename) == 0:
            return
        match ids:
            case "Chrome":
                self.lne_chrome.setText(filename)
            case "Edge":
                self.lne_edge.setText(filename)
            case "Brave":
                self.lne_brave.setText(filename)
            case "Plugin DB":
                self.lne_plg_db.setText(filename)

    def on_pbn_save_clicked(self):
        us = QtCore.QSettings()
        us.setValue("chrome_exec", self.lne_chrome.text())
        us.setValue("edge_exec", self.lne_edge.text())
        us.setValue("brave_exec", self.lne_brave.text())
        us.setValue("plg_db", self.lne_plg_db.text())
        self.accept()

    def on_pbn_remove_clicked(self):
        us = QtCore.QSettings()
        us.clear()
        self.accept()

    def on_pbn_cancel_clicked(self):
        self.reject()
