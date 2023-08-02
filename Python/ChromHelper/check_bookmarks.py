# code: utf8
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from jnlib.chromium_utils import get_exec_path

from scan_bookmarks import scan_bookmarks, delete_bookmark


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
        settings = QtCore.QSettings()
        chrome_exec = settings.value("chrome_exec", "")  # type: str | object
        if len(chrome_exec) == 0 or not Path(chrome_exec).exists():
            chrome_exec = get_exec_path("chrome")
        edge_exec = settings.value("edge_exec", "")  # type: str | object
        if len(edge_exec) == 0 or not Path(edge_exec).exists():
            edge_exec = get_exec_path("edge")
        brave_exec = settings.value("brave_exec", "")  # type: str | object
        if len(brave_exec) == 0 or not Path(brave_exec).exists():
            brave_exec = get_exec_path("brave")

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
            r = delete_bookmark(self._current_browser, pi.strip(), self.lne_url.text())
            if r:
                s += 1
            else:
                f += 1

        QtWidgets.QMessageBox.information(self, "信息", f"成功删除 {s} 个，失败 {f} 个。")
        self.accept()


class UiCheckBookmarksWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_filter = QtWidgets.QLabel("输入关键词：", window)
        self.lne_filter = QtWidgets.QLineEdit(window)
        self.cbx_filter_by_url = QtWidgets.QCheckBox("搜索 URL", window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.hly_top.addWidget(self.lb_filter)
        self.hly_top.addWidget(self.lne_filter)
        self.hly_top.addWidget(self.cbx_filter_by_url)
        self.hly_top.addWidget(self.pbn_update)

        self.lw_bookmarks = QtWidgets.QListWidget(window)
        self.vly_m.addWidget(self.lw_bookmarks)


class CheckBookmarksWin(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiCheckBookmarksWin(self)
        self.browser = browser
        self._bmx_db = {}
        self._bmx_mp = {}  # type: dict[str, str]

        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.ui.lne_filter.textEdited.connect(self.on_lne_filter_text_edited)
        self.ui.cbx_filter_by_url.stateChanged.connect(self.on_cbx_filter_by_url_state_changed)
        self.ui.lw_bookmarks.itemDoubleClicked.connect(self.on_lw_bookmarks_item_double_clicked)

    def on_browser_changed(self, browser: str):
        self.browser = browser
        self._bmx_db, self._bmx_mp = scan_bookmarks(browser)
        self.ui.lw_bookmarks.clear()
        self.ui.lw_bookmarks.addItems(list(self._bmx_mp.keys()))
        self.ui.lne_filter.clear()

    def on_pbn_update_clicked(self):
        self.ui.lne_filter.clear()
        self.on_browser_changed(self.browser)

    def on_lne_filter_text_edited(self, text: str):
        if len(text) == 0:
            self.on_pbn_update_clicked()
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
        browser = self.browser
        spwin = ShowProfilesWin(browser, self)
        spwin.setWindowTitle(f"{title} - {browser}")
        url = self._bmx_mp[bookmark]
        profiles_pos = self._bmx_db[url]["profiles_pos"]

        display_profiles = []
        for prf, pos in profiles_pos:
            display_profiles.append(f"{prf:<12} - {pos}")

        spwin.update_list(display_profiles, url)
        spwin.show()
