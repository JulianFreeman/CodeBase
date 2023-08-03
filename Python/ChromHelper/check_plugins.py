# code: utf8
from typing import cast
from os import PathLike
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from jnlib.pyside6_utils import PushButtonWithId, change_font, HorizontalLine

from scan_extensions import scan_extensions
from show_profiles import ShowProfilesWin


class CheckPluginsWin(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.browser = browser
        self.vly_m = QtWidgets.QVBoxLayout()

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.cbx_safe = QtWidgets.QCheckBox("安全", self)
        self.cbx_unsafe = QtWidgets.QCheckBox("不安全", self)
        self.cbx_unknown = QtWidgets.QCheckBox("未知", self)
        self.cbx_safe.setChecked(True)
        self.cbx_unsafe.setChecked(True)
        self.cbx_unknown.setChecked(True)
        self.pbn_update = QtWidgets.QPushButton("更新", self)
        self.hly_top.addWidget(self.cbx_safe)
        self.hly_top.addWidget(self.cbx_unsafe)
        self.hly_top.addWidget(self.cbx_unknown)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_update)

        self.hln_top = HorizontalLine(self)
        self.vly_m.addWidget(self.hln_top)

        self.sa_plgs = QtWidgets.QScrollArea(self)
        self.sa_plgs.setWidgetResizable(True)
        self.sa_plgs.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.wg_sa_plgs = QtWidgets.QWidget()
        self.vly_wg_sa_plgs = QtWidgets.QVBoxLayout()
        self.vly_wg_sa_plgs.addStretch(1)
        self.wg_sa_plgs.setLayout(self.vly_wg_sa_plgs)
        self.sa_plgs.setWidget(self.wg_sa_plgs)

        self.vly_m.addWidget(self.sa_plgs)
        self.setLayout(self.vly_m)

        self.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.cbx_safe.stateChanged.connect(self.on_cbx_safe_state_changed)
        self.cbx_unsafe.stateChanged.connect(self.on_cbx_unsafe_state_changed)
        self.cbx_unknown.stateChanged.connect(self.on_cbx_unknown_state_changed)

        self._ext_db = {}
        self._current_widgets = []  # type: list[list[QtWidgets.QWidget]]

    def _gen_ext_info(self, ext_db: dict[str, dict]):
        self._ext_db = ext_db
        status_map = {
            True: 1,
            False: -1,
            None: 0,
        }

        for line in self._current_widgets[::-1]:
            for w in line:
                w.close()
            line.clear()
        self._current_widgets.clear()

        for i, p in enumerate(ext_db):
            wg_line = self._create_line_widget(self.wg_sa_plgs, f"wg_line_{i}")

            lb_icon = self._create_icon_label(wg_line, ext_db[p]["icon"])
            lb_name = self._create_name_label(wg_line, ext_db[p]["name"])
            lb_status = self._create_status_label(wg_line, status_map[ext_db[p]["safe"]])
            lb_status.setToolTip(ext_db[p]["note"])
            pbn_show = self._create_show_button(wg_line, f"pbn_show_{i}", p)
            pbn_show.clicked_with_id.connect(self.on_pbn_show_n_clicked_with_id)

            hly_line = QtWidgets.QHBoxLayout()
            hly_line.addWidget(lb_icon)
            hly_line.addWidget(lb_name)
            hly_line.addWidget(lb_status)
            hly_line.addWidget(pbn_show)
            hly_line.setContentsMargins(0, 0, 0, 0)
            wg_line.setLayout(hly_line)

            self.vly_wg_sa_plgs.insertWidget(0, wg_line)

            self._current_widgets.append([wg_line, lb_icon, lb_name, lb_status, pbn_show])

    def update_browser(self, browser: str):
        ext_db = scan_extensions(browser)
        self._gen_ext_info(ext_db)

    def on_cbx_safe_state_changed(self, state: int):
        show = QtCore.Qt.CheckState(state) == QtCore.Qt.CheckState.Checked
        for line in self._current_widgets:
            wg_line = line[0]
            lb_status = cast(QtWidgets.QLabel, line[3])
            if lb_status.property("status") > 0:
                wg_line.setVisible(show)

    def on_cbx_unsafe_state_changed(self, state: int):
        show = QtCore.Qt.CheckState(state) == QtCore.Qt.CheckState.Checked
        for line in self._current_widgets:
            wg_line = line[0]
            lb_status = cast(QtWidgets.QLabel, line[3])
            if lb_status.property("status") < 0:
                wg_line.setVisible(show)

    def on_cbx_unknown_state_changed(self, state: int):
        show = QtCore.Qt.CheckState(state) == QtCore.Qt.CheckState.Checked
        for line in self._current_widgets:
            wg_line = line[0]
            lb_status = cast(QtWidgets.QLabel, line[3])
            if lb_status.property("status") == 0:
                wg_line.setVisible(show)

    def on_pbn_update_clicked(self):
        self.update_browser(self.browser)
        QtWidgets.QMessageBox.information(self, "提示", "插件信息已更新。")

    def on_pbn_show_n_clicked_with_id(self, ids: str):
        profiles = self._ext_db[ids]["profiles"]  # type: list[str]
        browser = self.browser
        spwin = ShowProfilesWin(browser, "plugins", self)
        spwin.setWindowTitle(f'{self._ext_db[ids]["name"]} - {browser}')

        icon = self._ext_db[ids]["icon"]
        if len(icon) != 0:
            spwin.setWindowIcon(QtGui.QPixmap(icon).scaled(
                16, 16, mode=QtCore.Qt.TransformationMode.SmoothTransformation))

        display_profiles = []
        for p in profiles:
            pi, pn = p.split("%", 1)
            display_profiles.append(f"{pi:<12} - {pn}")

        spwin.update_list(display_profiles, ids)
        spwin.show()

    def on_browser_changed(self, browser: str):
        self.browser = browser
        self.update_browser(browser)

    @staticmethod
    def _create_line_widget(window: QtWidgets.QWidget, obj_name: str, rad=4) -> QtWidgets.QWidget:
        wg_ln = QtWidgets.QWidget(window)
        wg_ln.setObjectName(obj_name)
        wg_ln.setStyleSheet(f"""
        #{obj_name} {{
            border-radius: {rad}px;
            background-color: #EDEDED;
        }}
        #{obj_name}:hover {{
            background-color: #E3E3E3;
        }}
        """)
        wg_ln.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        return wg_ln

    @staticmethod
    def _create_icon_label(window: QtWidgets.QWidget, icon: str | PathLike | QtGui.QPixmap,
                           rad=4, bw=2) -> QtWidgets.QLabel:
        lb_i = QtWidgets.QLabel(window)
        lb_i.setStyleSheet(f"""
            border-radius: {rad}px;
            border: {bw}px solid #9EA2AB;
        """)
        if isinstance(icon, QtGui.QPixmap):
            pix = icon
        elif len(icon) != 0 and Path(icon).exists():
            pix = QtGui.QPixmap(icon).scaled(32, 32, mode=QtCore.Qt.TransformationMode.SmoothTransformation)
        else:
            pix = QtGui.QPixmap(32, 32)
            pix.fill("white")

        lb_i.setPixmap(pix)
        lb_i.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        return lb_i

    @staticmethod
    def _create_show_button(window: QtWidgets.QWidget, obj_name: str, ids: str,
                            family="DengXian", size=12, vpad=8, hpad=10, rad=4, bw=2) -> PushButtonWithId:
        pbn_s = PushButtonWithId(ids, window)
        pbn_s.setObjectName(obj_name)
        pbn_s.setText("显示用户")
        change_font(pbn_s, family, size)
        pbn_s.setStyleSheet(f"""
        #{obj_name} {{
            color: #1A1B1C;
            padding: {vpad}px {hpad}px;
            border-radius: {rad}px;
            border: {bw}px solid #9EA2AB;
        }}
        #{obj_name}:hover {{
            color: #1438AB;
            background-color: #4DF8FF;
            border-color: #1438AB;
        }}
        #{obj_name}:pressed {{
            color: cyan;
            background-color: blue;
        }}
        """)
        pbn_s.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        pbn_s.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        return pbn_s

    @staticmethod
    def _create_name_label(window: QtWidgets.QWidget, name: str,
                           family="DengXian", size=12, vpad=4, hpad=6, rad=4, bw=2) -> QtWidgets.QLabel:
        lb_n = QtWidgets.QLabel(window)
        change_font(lb_n, family, size)
        lb_n.setStyleSheet(f"""
            color: #1A1B1C;
            padding: {vpad}px {hpad}px;
            border-radius: {rad}px;
            border: {bw}px solid #9EA2AB;
        """)

        lb_n.setText(name)
        lb_n.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        lb_n.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        return lb_n

    @staticmethod
    def _create_status_label(window: QtWidgets.QWidget, status: int,
                             family="DengXian", size=12, vpad=4, hpad=6, rad=4, bw=2) -> QtWidgets.QLabel:
        lb_s = QtWidgets.QLabel(window)
        change_font(lb_s, family, size)
        if status > 0:
            lb_s.setText("安　全")
            lb_s.setStyleSheet(f"""
                color: #14613D;
                background-color: #00EB00;
                padding: {vpad}px {hpad}px;
                border-radius: {rad}px;
                border: {bw}px solid #9EA2AB;
            """)
        elif status < 0:
            lb_s.setText("不安全")
            lb_s.setStyleSheet(f"""
                color: #F1FFD6;
                background-color: #B00F0F;
                padding: {vpad}px {hpad}px;
                border-radius: {rad}px;
                border: {bw}px solid #9EA2AB;
            """)
        else:
            lb_s.setText("未　知")
            lb_s.setStyleSheet(f"""
                color: #2C302D;
                background-color: #AFBDB6;
                padding: {vpad}px {hpad}px;
                border-radius: {rad}px;
                border: {bw}px solid #9EA2AB;
            """)
        lb_s.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        lb_s.setProperty("status", status)
        return lb_s
