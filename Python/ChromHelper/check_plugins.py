# code: utf8
import json
from typing import cast
from os import PathLike
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from jnlib.pyside6_utils import PushButtonWithId, change_font, accept_warning

from scan_extensions import scan_extensions
from show_profiles import ShowProfilesWin
from animated_toggle import AnimatedToggle


class CheckPluginsWin(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.browser = browser
        self.vly_m = QtWidgets.QVBoxLayout()

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.cbx_safe = AnimatedToggle(self, checked_color="#008B00")
        self.cbx_unsafe = AnimatedToggle(self, checked_color="#B00F0F")
        self.cbx_unknown = AnimatedToggle(self, checked_color="#6C6C6C")
        self.cbx_safe.setChecked(True)
        self.cbx_unsafe.setChecked(True)
        self.cbx_unknown.setChecked(True)
        self.pbn_update = self._create_button(self, "pbn_update", "更　新", is_show=False)
        self.pbn_export_unknown = self._create_button(self, "pbn_export_unknown", "导出未知", is_show=False)
        self.hly_top.addWidget(self.cbx_safe)
        self.hly_top.addWidget(self.cbx_unsafe)
        self.hly_top.addWidget(self.cbx_unknown)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_update)
        self.hly_top.addWidget(self.pbn_export_unknown)

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

        self.cbx_safe.stateChanged.connect(self.on_cbx_safe_state_changed)
        self.cbx_unsafe.stateChanged.connect(self.on_cbx_unsafe_state_changed)
        self.cbx_unknown.stateChanged.connect(self.on_cbx_unknown_state_changed)
        self.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.pbn_export_unknown.clicked.connect(self.on_pbn_export_unknown_clicked)

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
            pbn_show = self._create_button(wg_line, f"pbn_show_{i}", p, is_show=True)
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

    def on_pbn_export_unknown_clicked(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "导出未知")
        if len(dirname) == 0:
            return
        ex_file = Path(dirname, f"unknown_extensions_{self.browser}.json")
        if accept_warning(self, ex_file.exists(), "警告", "文件已存在，确认覆盖吗？"):
            return

        unknown_ext = {e: v["name"] for e, v in self._ext_db.items() if v["safe"] is None}
        with open(ex_file, "w", encoding="utf8") as f:
            json.dump(unknown_ext, f, indent=4, ensure_ascii=False)
        QtWidgets.QMessageBox.information(self, "提示", f"已导出到 {ex_file}")

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
        self.on_cbx_safe_state_changed(self.cbx_safe.checkState().value)
        self.on_cbx_unsafe_state_changed(self.cbx_unsafe.checkState().value)
        self.on_cbx_unknown_state_changed(self.cbx_unknown.checkState().value)

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
    def _create_button(window: QtWidgets.QWidget, obj_name: str, info: str,
                       family="Noto Sans", size=12, vpad=8, hpad=10, rad=4, bw=2,
                       *, is_show: bool) -> QtWidgets.QPushButton | PushButtonWithId:
        if is_show:
            pbn_1 = PushButtonWithId(info, window)
            pbn_1.setText("显示用户")
            pbn_1.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        else:
            pbn_1 = QtWidgets.QPushButton(info, window)

        pbn_1.setObjectName(obj_name)
        change_font(pbn_1, family, size)
        pbn_1.setStyleSheet(f"""
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
        pbn_1.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        return pbn_1

    @staticmethod
    def _create_name_label(window: QtWidgets.QWidget, name: str,
                           family="Noto Sans", size=12, vpad=4, hpad=6, rad=4, bw=2) -> QtWidgets.QLabel:
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
                             family="Noto Sans", size=12, vpad=4, hpad=6, rad=4, bw=2) -> QtWidgets.QLabel:
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
