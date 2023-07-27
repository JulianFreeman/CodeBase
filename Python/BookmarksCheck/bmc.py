# code: utf8

# Change log
#
# v1.1
# 1. 支持删除书签
#
# v1.0
# 1. 初始版本
#

#########################
#  ____  __  __  _____  #
# |  _ \|  \/  |/ ____| #
# | |_) | \  / | |      #
# |  _ <| |\/| | |      #
# | |_) | |  | | |____  #
# |____/|_|  |_|\_____| #
#########################

import sys
from pathlib import Path

from PySide6 import QtWidgets, QtCore, QtGui
from scan_bookmarks import scan_bookmarks, delete_bookmark

import bmc_rc


version = [1, 0, 20230716]

_BROWSERS = ["Chrome", "Edge", "Brave"]

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
        self.vly_m.addLayout(self.hly_bot)
        self.vly_m.addStretch(1)
        self.setLayout(self.vly_m)

        self.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.pbn_remove.clicked.connect(self.on_pbn_remove_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)
        self.pbn_chrome.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)
        self.pbn_edge.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)
        self.pbn_brave.clicked_with_id.connect(self.on_pbn_n_clicked_with_id)

        self._read_settings()

    def _read_settings(self):
        settings = QtCore.QSettings("JnPrograms", "BPC")
        chrome_exec = settings.value("chrome_exec", "")  # type: str | object
        edge_exec = settings.value("edge_exec", "")  # type: str | object
        brave_exec = settings.value("brave_exec", "")  # type: str | object
        self.lne_chrome.setText(chrome_exec)
        self.lne_edge.setText(edge_exec)
        self.lne_brave.setText(brave_exec)

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

    def on_pbn_save_clicked(self):
        us = QtCore.QSettings("JnPrograms", "BPC")
        us.setValue("chrome_exec", self.lne_chrome.text())
        us.setValue("edge_exec", self.lne_edge.text())
        us.setValue("brave_exec", self.lne_brave.text())
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
        self.setLayout(self.vly_m)

        self.lne_url = QtWidgets.QLineEdit(self)
        self.lne_url.setReadOnly(True)
        self.vly_m.addWidget(self.lne_url)

        self.lw_profiles = QtWidgets.QListWidget(self)
        self.lw_profiles.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.vly_m.addWidget(self.lw_profiles)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_open = QtWidgets.QPushButton("打开", self)
        self.pbn_delete_all = QtWidgets.QPushButton("删除所有", self)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_open)
        self.hly_bot.addWidget(self.pbn_delete_all)
        self.vly_m.addLayout(self.hly_bot)

        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.pbn_delete_all.clicked.connect(self.on_pbn_delete_all_clicked)

        self._process = QtCore.QProcess(self)
        self._current_browser = browser

    def update_list(self, profiles: list[str, ...], url: str):
        profiles.sort(key=lambda x: 0 if x.split(" ", 1)[0] == "Default" else int(x.split(" - ")[0].split(" ")[1]))

        self.lw_profiles.clear()
        self.lw_profiles.addItems(profiles)
        self.lne_url.setText(url)

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

    def on_pbn_delete_all_clicked(self):
        s, f = 0, 0
        for i in range(self.lw_profiles.count()):
            item = self.lw_profiles.item(i)
            pi, _ = item.text().split(" - ", 1)  # type: str, str
            r, _ = delete_bookmark(self._current_browser, pi.strip(), self.lne_url.text())
            if r:
                s += 1
            else:
                f += 1

        QtWidgets.QMessageBox.information(self, "信息", f"成功删除 {s} 个，失败 {f} 个。")
        self.accept()


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(640, 360)
        window.setWindowTitle("检查浏览器书签")
        window.setWindowIcon(QtGui.QIcon(":/bmc_16.png"))

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_browsers = QtWidgets.QLabel("切换浏览器：", window)
        self.hly_top.addWidget(self.lb_browsers)
        self.cmbx_browsers = QtWidgets.QComboBox(window)
        self.cmbx_browsers.addItems(_BROWSERS)
        self.hly_top.addWidget(self.cmbx_browsers)
        self.hly_top.addStretch(1)
        self.pbn_refresh = QtWidgets.QPushButton("更新", window)
        self.hly_top.addWidget(self.pbn_refresh)
        self.pbn_settings = QtWidgets.QPushButton("设置", window)
        self.hly_top.addWidget(self.pbn_settings)

        self.hly_filter = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_filter)

        self.lb_filter = QtWidgets.QLabel("输入关键词：", window)
        self.hly_filter.addWidget(self.lb_filter)
        self.lne_filter = QtWidgets.QLineEdit(window)
        self.hly_filter.addWidget(self.lne_filter)
        self.cbx_filter_by_url = QtWidgets.QCheckBox("搜索 URL", window)
        self.hly_filter.addWidget(self.cbx_filter_by_url)

        self.lw_bookmarks = QtWidgets.QListWidget(window)
        self.vly_m.addWidget(self.lw_bookmarks)


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)
        self._bmx_db = {}
        self._bmx_mp = {}  # type: dict[str, str]

        self.on_cmbx_browsers_current_index_changed(0)
        self.ui.cmbx_browsers.currentIndexChanged.connect(self.on_cmbx_browsers_current_index_changed)
        self.ui.pbn_refresh.clicked.connect(self.on_pbn_refresh_clicked)
        self.ui.pbn_settings.clicked.connect(self.on_pbn_settings_clicked)
        self.ui.lne_filter.textEdited.connect(self.on_lne_filter_text_edited)
        self.ui.cbx_filter_by_url.stateChanged.connect(self.on_cbx_filter_by_url_state_changed)
        self.ui.lw_bookmarks.itemDoubleClicked.connect(self.on_lw_bookmarks_item_double_clicked)

    def on_cmbx_browsers_current_index_changed(self, index: int):
        self._bmx_db, self._bmx_mp = scan_bookmarks(_BROWSERS[index])
        self.ui.lw_bookmarks.clear()
        self.ui.lw_bookmarks.addItems(list(self._bmx_mp.keys()))
        self.ui.lne_filter.clear()

    def on_pbn_refresh_clicked(self):
        self.ui.lne_filter.clear()
        self.on_cmbx_browsers_current_index_changed(self.ui.cmbx_browsers.currentIndex())

    def on_pbn_settings_clicked(self):
        stwin = SettingsWin(self)
        stwin.exec()

    def on_lne_filter_text_edited(self, text: str):
        if len(text) == 0:
            self.on_pbn_refresh_clicked()
            return

        self.ui.lw_bookmarks.clear()
        by_url = self.ui.cbx_filter_by_url.checkState() == QtCore.Qt.CheckState.Checked
        text = text.lower()
        if by_url:
            filtered_bookmarks = [b for b in self._bmx_mp if text in self._bmx_mp[b].lower()]
        else:
            filtered_bookmarks = [b for b in self._bmx_mp if text in b.lower()]
        self.ui.lw_bookmarks.addItems(filtered_bookmarks)

    def on_cbx_filter_by_url_state_changed(self, state: int):
        self.on_lne_filter_text_edited(self.ui.lne_filter.text())

    def on_lw_bookmarks_item_double_clicked(self, item: QtWidgets.QListWidgetItem):
        bookmark = item.text()
        if len(bookmark) > 40:
            title = bookmark[:37] + "..."
        else:
            title = bookmark
        browser = self.ui.cmbx_browsers.currentText()
        spwin = ShowProfilesWin(browser, self)
        spwin.setWindowTitle(f"{title} - {browser}")
        url = self._bmx_mp[bookmark]
        profiles_pos = self._bmx_db[url]["profiles_pos"]

        display_profiles = []
        for prf, pos in profiles_pos:
            display_profiles.append(f"{prf:<12} - {pos}")

        spwin.update_list(display_profiles, url)
        spwin.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
