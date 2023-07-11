# code: utf8

# Change log
#
# v1.0
# 1. 支持 Mac 系统
# 2. 其他微调
#
# v0.1
# 1. 只支持 Windows 系统
# 2. 只支持 Chrome，Edge，Brave 浏览器
#

#########################
#  ____  _____   _____  #
# |  _ \|  __ \ / ____| #
# | |_) | |__) | |      #
# |  _ <|  ___/| |      #
# | |_) | |    | |____  #
# |____/|_|     \_____| #
#########################

import sys
from os import PathLike
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from scanplg import scan_google_plugins
import brwplgc_rc

version = (1, 0, 20230711)


default_browser_exec = {
    "win32": {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    },
    "darwin": {
        "chrome": r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "edge": r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "brave": r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    },
}


def _change_font(widget: QtWidgets.QWidget, family: str, size: int, bold=True):
    font = widget.font()
    font.setFamily(family)
    font.setPointSize(size)
    font.setBold(bold)
    widget.setFont(font)


class PushButtonWithId(QtWidgets.QPushButton):

    clicked_with_id = QtCore.Signal(str)

    def __init__(self, ids: str, parent: QtWidgets.QWidget | None = None, title: str = ""):
        super().__init__(title, parent)
        self.ids = ids
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_id.emit(self.ids)


class SettingsWin(QtWidgets.QDialog):

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

        self.hln_1 = QtWidgets.QFrame(self)
        self.hln_1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.hln_1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        self.gly_paths.addWidget(self.hln_1, 3, 0, 1, 3)

        self.gly_paths.addWidget(self.lb_plg_db, 4, 0)
        self.gly_paths.addWidget(self.lne_plg_db, 4, 1)
        self.gly_paths.addWidget(self.pbn_plg_db, 4, 2)

        self.hln_2 = QtWidgets.QFrame(self)
        self.hln_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.hln_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_save = QtWidgets.QPushButton("保存", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)
        self.pbn_remove = QtWidgets.QPushButton("清除", self)

        self.lb_version = QtWidgets.QLabel(self)
        self.lb_version.setText(f"版本：v{version[0]}.{version[1]}，日期：{version[-1]}")

        self.hly_bot.addWidget(self.lb_version)
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
        settings = QtCore.QSettings("JnPrograms", "BPC")
        chrome_exec = settings.value("chrome_exec", "")  # type: str | object
        edge_exec = settings.value("edge_exec", "")  # type: str | object
        brave_exec = settings.value("brave_exec", "")  # type: str | object
        plg_db = settings.value("plg_db", "")  # type: str | object
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
        us = QtCore.QSettings("JnPrograms", "BPC")
        us.setValue("chrome_exec", self.lne_chrome.text())
        us.setValue("edge_exec", self.lne_edge.text())
        us.setValue("brave_exec", self.lne_brave.text())
        us.setValue("plg_db", self.lne_plg_db.text())
        self.accept()

    def on_pbn_remove_clicked(self):
        us = QtCore.QSettings("JnPrograms", "BPC")
        us.clear()
        self.accept()

    def on_pbn_cancel_clicked(self):
        self.reject()


class ShowProfilesWin(QtWidgets.QDialog):

    def __init__(self, browser: str, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.resize(400, 360)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.lw_profiles = QtWidgets.QListWidget(self)
        self.lw_profiles.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        _change_font(self.lw_profiles, "Consolas", 12, False)

        self.pbn_open = QtWidgets.QPushButton("打开", self)
        _change_font(self.pbn_open, "DengXian", 12, True)

        self.vly_m.addWidget(self.lw_profiles)
        self.vly_m.addWidget(self.pbn_open)
        self.setLayout(self.vly_m)

        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)

        self._process = QtCore.QProcess(self)
        self._current_browser = browser

    def update_list(self, profiles: list[str, ...]):
        profiles.sort(key=lambda x: 0 if x.split(" ", 1)[0] == "Default" else int(x.split(" - ")[0].split(" ")[1]))

        self.lw_profiles.clear()
        self.lw_profiles.addItems(profiles)

    def on_pbn_open_clicked(self):
        plat = sys.platform
        settings = QtCore.QSettings("JnPrograms", "BPC")
        chrome_exec = settings.value("chrome_exec", "")  # type: str | object
        if len(chrome_exec) == 0 or not Path(chrome_exec).exists():
            chrome_exec = default_browser_exec[plat]["chrome"]
        edge_exec = settings.value("edge_exec", "")  # type: str | object
        if len(edge_exec) == 0 or not Path(edge_exec).exists():
            edge_exec = default_browser_exec[plat]["edge"]
        brave_exec = settings.value("brave_exec", "")  # type: str | object
        if len(brave_exec) == 0 or not Path(brave_exec).exists():
            brave_exec = default_browser_exec[plat]["brave"]

        profiles = self.lw_profiles.selectedItems()
        if self._current_browser == "Chrome":
            cmd = rf'"{chrome_exec}" --profile-directory="{{0}}"'
        elif self._current_browser == "Edge":
            cmd = rf'"{edge_exec}" --profile-directory="{{0}}"'
        elif self._current_browser == "Brave":
            cmd = rf'"{brave_exec}" --profile-directory="{{0}}"'
        else:
            return

        for p in profiles:
            pi, _ = p.text().split(" - ", 1)  # type: str, str
            self._process.startCommand(cmd.format(pi.strip()))
            self._process.waitForFinished(10000)


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self._BROWSERS = ["Chrome", "Edge", "Brave"]
        self._BROWSERS_ICON = [
            QtGui.QPixmap(":/imgs/Dtafalonso-Android-L-Chrome.32.png"),
            QtGui.QPixmap(":/imgs/Dtafalonso-Win-10x-Edge.32.png"),
            QtGui.QPixmap(":/imgs/Papirus-Team-Papirus-Apps-Brave.32.png"),
        ]

        self.resize(640, 540)
        self.setWindowTitle("浏览器插件检查")
        self.setWindowIcon(QtGui.QIcon(":/imgs/Franksouza183-Fs-Mimetypes-extension.16.png"))

        self.vly_m = QtWidgets.QVBoxLayout()

        self.hly_top = QtWidgets.QHBoxLayout()
        self.lb_brw_ico = self._create_icon_label(self, self._BROWSERS_ICON[0])

        self.cmbx_browsers = QtWidgets.QComboBox(self)
        self.cmbx_browsers.setObjectName("cmbx_browsers")
        self.cmbx_browsers.addItems(self._BROWSERS)
        _change_font(self.cmbx_browsers, "DengXian", 12)
        self.cmbx_browsers.setStyleSheet("""
        #cmbx_browsers {
            padding: 8px 10px;
            border-radius: 4px;
            border: 2px solid #9EA2AB;
        }
        #cmbx_browsers:drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
        
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: solid;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            
            background-color: #EDEDED;
        }
        #cmbx_browsers:drop-down:on {
            background-color: #E3E3E3;
        }
        #cmbx_browsers:down-arrow {
            image: url(:/imgs/chevron-down-outline_16.png);
        }
        """)

        self.pbn_settings = QtWidgets.QPushButton(self)
        self.pbn_settings.setObjectName("pbn_settings")
        _change_font(self.pbn_settings, "DengXian", 12)
        self.pbn_settings.setText("设置")
        self.pbn_settings.setStyleSheet("""
        #pbn_settings {
            color: #1A1B1C;
            padding: 7px 10px;
            border-radius: 4px;
            border: 2px solid #9EA2AB;
        }
        #pbn_settings:hover {
            color: #1438AB;
            background-color: #4DF8FF;
            border-color: #1438AB;
        }
        #pbn_settings:pressed {
            color: cyan;
            background-color: blue;
        }
        """)
        self.pbn_settings.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        self.hly_top.addWidget(self.lb_brw_ico)
        self.hly_top.addWidget(self.cmbx_browsers)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_settings)

        self.sa_plgs = QtWidgets.QScrollArea(self)
        self.sa_plgs.setWidgetResizable(True)
        self.wg_sa_plgs = QtWidgets.QWidget()
        self.vly_wg_sa_plgs = QtWidgets.QVBoxLayout()
        self.vly_wg_sa_plgs.addStretch(1)
        self.wg_sa_plgs.setLayout(self.vly_wg_sa_plgs)
        self.sa_plgs.setWidget(self.wg_sa_plgs)

        self.vly_m.addLayout(self.hly_top)
        self.vly_m.addWidget(self.sa_plgs)

        self.setLayout(self.vly_m)

        self._ext_db = {}

        self._current_widgets = []  # type: list[QtWidgets.QWidget, ...]

        self.cmbx_browsers.currentIndexChanged.connect(self.on_cmbx_browsers_current_index_changed)
        self.pbn_settings.clicked.connect(self.on_pbn_settings_clicked)

        self.update_browser(self._BROWSERS[0])

    def _gen_ext_info(self, ext_db: dict[str, dict]):
        self._ext_db = ext_db
        status_map = {
            True: 1,
            False: -1,
            None: 0,
        }

        for w in self._current_widgets[::-1]:
            w.close()
        self._current_widgets.clear()

        for i, p in enumerate(ext_db):
            wg_line = self._create_line_widget(self.wg_sa_plgs, f"wg_line_{i}")

            lb_icon = self._create_icon_label(wg_line, ext_db[p]["icon"])
            lb_name = self._create_name_label(wg_line, ext_db[p]["name"])
            lb_status = self._create_status_label(wg_line, status_map[ext_db[p]["safe"]])
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

            self._current_widgets.extend([wg_line, lb_icon, lb_name, lb_status, pbn_show])

    def update_browser(self, browser: str):
        ext_db = scan_google_plugins(browser)
        self._gen_ext_info(ext_db)

    def on_pbn_settings_clicked(self):
        stwin = SettingsWin(self)
        stwin.exec()

    def on_pbn_show_n_clicked_with_id(self, ids: str):
        profiles = self._ext_db[ids]["profiles"]  # type: list[str, ...]
        browser = self.cmbx_browsers.currentText()
        spwin = ShowProfilesWin(browser, self)
        spwin.setWindowTitle(f'{self._ext_db[ids]["name"]} - {browser}')

        icon = self._ext_db[ids]["icon"]
        if len(icon) != 0:
            spwin.setWindowIcon(QtGui.QPixmap(icon).scaled(
                16, 16, mode=QtCore.Qt.TransformationMode.SmoothTransformation))

        display_profiles = []
        for p in profiles:
            pi, pn = p.split("%", 1)
            display_profiles.append(f"{pi:<12} - {pn}")

        spwin.update_list(display_profiles)
        spwin.show()

    def on_cmbx_browsers_current_index_changed(self):
        i = self.cmbx_browsers.currentIndex()
        self.lb_brw_ico.setPixmap(self._BROWSERS_ICON[i])
        self.update_browser(self._BROWSERS[i])

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
        _change_font(pbn_s, family, size)
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
        _change_font(lb_n, family, size)
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
        _change_font(lb_s, family, size)
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
        return lb_s


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
