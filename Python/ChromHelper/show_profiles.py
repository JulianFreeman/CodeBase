# code: utf8
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from jnlib.chromium_utils import get_exec_path
from jnlib.pyside6_utils import accept_warning

from scan_bookmarks import delete_bookmark
from scan_extensions import delete_extension


class ShowProfilesWin(QtWidgets.QDialog):

    def __init__(self, browser: str, kind: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.kind = kind
        self.browser = browser
        self.resize(400, 360)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.lne_info = QtWidgets.QLineEdit(self)
        self.lne_info.setReadOnly(True)
        self.vly_m.addWidget(self.lne_info)

        self.lw_profiles = QtWidgets.QListWidget(self)
        self.lw_profiles.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.vly_m.addWidget(self.lw_profiles)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.pbn_open = QtWidgets.QPushButton("打开", self)
        self.pbn_delete_selected = QtWidgets.QPushButton("删除所选", self)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_open)
        self.hly_bot.addWidget(self.pbn_delete_selected)
        self.vly_m.addLayout(self.hly_bot)

        self.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.pbn_delete_selected.clicked.connect(self.on_pbn_delete_selected_clicked)

        self._process = QtCore.QProcess(self)

    def update_list(self, profiles: list[str], info: str):
        profiles.sort(key=lambda x: 0 if x.split(" ", 1)[0] == "Default" else int(x.split(" - ")[0].split(" ", 1)[1]))

        self.lw_profiles.clear()
        self.lw_profiles.addItems(profiles)
        self.lne_info.setText(info)

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
        pro_map = {
            "Chrome": chrome_exec,
            "Edge": edge_exec,
            "Brave": brave_exec,
        }
        pro = pro_map.get(self.browser, None)
        if pro is None or not Path(pro).exists():
            QtWidgets.QMessageBox.critical(self, "错误", f"未找到 {self.browser} 的执行文件路径。")
            return
        cmd = rf'"{pro}" --profile-directory="{{0}}"'

        for p in profiles:
            pi, _ = p.text().split(" - ", 1)  # type: str, str
            # start 不行，不知道为什么，莫名其妙
            self._process.startCommand(cmd.format(pi.strip()))
            self._process.waitForFinished(10000)

    def on_pbn_delete_selected_clicked(self):
        if accept_warning(self, True, "警告", "确定要删除所选吗？"):
            return

        success, fail, total = 0, 0, 0
        for item in self.lw_profiles.selectedItems():
            pi, _ = item.text().split(" - ", 1)  # type: str, str
            if self.kind == "bookmarks":
                r = delete_bookmark(self.browser, pi.strip(), self.lne_info.text())
            elif self.kind == "plugins":
                r = delete_extension(self.browser, pi.strip(), self.lne_info.text())
            else:
                continue

            if r:
                success += 1
            else:
                fail += 1
            total += 1

        QtWidgets.QMessageBox.information(self, "信息", f"一共选中 {total} 个，成功删除 {success} 个，失败 {fail} 个。")
        self.accept()
