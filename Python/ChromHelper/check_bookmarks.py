# code: utf8
from PySide6 import QtWidgets, QtCore

from show_profiles import ShowProfilesWin
from scan_bookmarks import scan_bookmarks


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
        QtWidgets.QMessageBox.information(self, "提示", "书签信息已更新。")

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
        spwin = ShowProfilesWin(browser, "bookmarks", self)
        spwin.setWindowTitle(f"{title} - {browser}")
        url = self._bmx_mp[bookmark]
        profiles_pos = self._bmx_db[url]["profiles_pos"]

        display_profiles = []
        for prf, pos in profiles_pos:
            display_profiles.append(f"{prf:<12} - {pos}")

        spwin.update_list(display_profiles, url)
        spwin.show()
