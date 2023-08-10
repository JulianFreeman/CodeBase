# code: utf8
from PySide6 import QtWidgets, QtCore, QtGui

from jnlib.pyside6_utils import accept_warning

from show_profiles import ShowProfilesWin
from export_bookmarks import ExportBookmarksWin
from scan_bookmarks import scan_bookmarks, delete_bookmark


class UiCheckBookmarksWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_filter = QtWidgets.QLabel("输入关键词：", window)
        self.lne_filter = QtWidgets.QLineEdit(window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.pbn_export_sel = QtWidgets.QPushButton("导出所选", window)
        self.pbn_delete_sel = QtWidgets.QPushButton("删除所选", window)
        self.hly_top.addWidget(self.lb_filter)
        self.hly_top.addWidget(self.lne_filter)
        self.hly_top.addWidget(self.pbn_update)
        self.hly_top.addWidget(self.pbn_export_sel)
        self.hly_top.addWidget(self.pbn_delete_sel)

        self.hly_mid = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_mid)

        self.cbx_filter_by_url = QtWidgets.QCheckBox("搜索 URL", window)
        self.cbx_exclude_search = QtWidgets.QCheckBox("排除 Google Search", window)
        self.lb_cur_amount = QtWidgets.QLabel("当前书签个数：", window)
        self.sbx_cur_amount = QtWidgets.QSpinBox(window)
        self.sbx_cur_amount.setReadOnly(True)
        self.sbx_cur_amount.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.sbx_cur_amount.setMaximum(9999)
        self.hly_mid.addWidget(self.cbx_filter_by_url)
        self.hly_mid.addWidget(self.cbx_exclude_search)
        self.hly_mid.addStretch(1)
        self.hly_mid.addWidget(self.lb_cur_amount)
        self.hly_mid.addWidget(self.sbx_cur_amount)

        self.lw_bookmarks = QtWidgets.QListWidget(window)
        self.lw_bookmarks.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.lw_bookmarks)


class CheckBookmarksWin(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.ui = UiCheckBookmarksWin(self)
        self.browser = browser
        self._bmx_db = {}
        self._bmx_mp = {}  # type: dict[str, str]

        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)
        self.ui.pbn_export_sel.clicked.connect(self.on_pbn_export_sel_clicked)
        self.ui.pbn_delete_sel.clicked.connect(self.on_pbn_delete_sel_clicked)
        self.ui.lne_filter.textEdited.connect(self.on_lne_filter_text_edited)
        self.ui.cbx_filter_by_url.stateChanged.connect(self.on_cbx_filter_by_url_state_changed)
        self.ui.cbx_exclude_search.stateChanged.connect(self.on_cbx_exclude_search_state_changed)
        self.ui.lw_bookmarks.itemDoubleClicked.connect(self.on_lw_bookmarks_item_double_clicked)

    def on_browser_changed(self, browser: str):
        self.browser = browser
        self._bmx_db, self._bmx_mp = scan_bookmarks(browser)
        self.ui.lw_bookmarks.clear()
        self.ui.lw_bookmarks.addItems(list(self._bmx_mp.keys()))
        # 为了触发过滤
        self.on_lne_filter_text_edited(self.ui.lne_filter.text())

    def on_pbn_update_clicked(self):
        self.on_browser_changed(self.browser)
        QtWidgets.QMessageBox.information(self, "提示", "书签信息已更新。")

    def on_pbn_delete_sel_clicked(self):
        if accept_warning(self, True, "警告", "确定删除所选吗？"):
            return

        sel_items = self.ui.lw_bookmarks.selectedItems()
        total, success, fail = 0, 0, 0
        for item in sel_items:
            bookmark = item.text()
            url = self._bmx_mp[bookmark]
            profiles_pos = self._bmx_db[url]["profiles_pos"]

            for prf, _ in profiles_pos:
                r = delete_bookmark(self.browser, prf, url)
                if r:
                    success += 1
                else:
                    fail += 1
                total += 1
        QtWidgets.QMessageBox.information(
            self, "信息",
            f"一共选中 {len(sel_items)} 个书签，共 {total} 个位置，成功删除 {success} 个，失败 {fail} 个。"
        )

    def on_pbn_export_sel_clicked(self):
        sel_items = [item.text() for item in self.ui.lw_bookmarks.selectedItems()]
        bmx_db = {url: info for url, info in self._bmx_db.items() if info["name"] in sel_items}

        ebw = ExportBookmarksWin(self.browser, self, bmx_db)
        ebw.setWindowTitle("导出书签")
        ebw.setWindowIcon(QtGui.QIcon(":/img/ebk_16.png"))
        ebw.resize(640, 360)
        ebw.exec()

    def on_lne_filter_text_edited(self, text: str):
        self.ui.lw_bookmarks.clear()
        if len(text) == 0:
            filtered_bmx = self._bmx_mp
        else:
            by_url = self.ui.cbx_filter_by_url.checkState() == QtCore.Qt.CheckState.Checked
            text = text.lower()
            if by_url:
                filtered_bmx = [b for b in self._bmx_mp if text in self._bmx_mp[b].lower()]
            else:
                filtered_bmx = [b for b in self._bmx_mp if text in b.lower()]
        if self.ui.cbx_exclude_search.checkState() == QtCore.Qt.CheckState.Checked:
            filtered_bmx = [b for b in filtered_bmx if not self._bmx_mp[b].startswith("https://www.google.com/search")]

        self.ui.lw_bookmarks.addItems(filtered_bmx)
        self.ui.sbx_cur_amount.setValue(len(filtered_bmx))

    def on_cbx_filter_by_url_state_changed(self, state: int):
        self.on_lne_filter_text_edited(self.ui.lne_filter.text())

    def on_cbx_exclude_search_state_changed(self, state: int):
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
