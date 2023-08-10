# code: utf8
import sys
import shutil
from pathlib import Path
from PySide6 import QtWidgets, QtGui

from jnlib.general_utils import get_log_dir

from chrom_settings import ChromSettingsWin
from check_plugins import CheckPluginsWin
from check_bookmarks import CheckBookmarksWin
from check_settings import CheckSettingsWin

import chrom_helper_rc


class UiChromHelperMainWin(object):

    def __init__(self, window: QtWidgets.QMainWindow):
        icons = {
            "chrome": QtGui.QIcon(":/img/chrome_32.png"),
            "edge": QtGui.QIcon(":/img/edge_32.png"),
            "brave": QtGui.QIcon(":/img/brave_32.png"),
            "bsc": QtGui.QIcon(":/img/bsc_16.png"),
            "bpc": QtGui.QIcon(":/img/bpc_16.png"),
            "bmc": QtGui.QIcon(":/img/bmc_16.png"),
        }

        window.resize(860, 680)
        window.setWindowTitle("Chromium 核心浏览器辅助工具")
        window.setWindowIcon(QtGui.QIcon(":/img/chrom_helper_64.png"))

        self.tw_cw = QtWidgets.QTabWidget(window)
        if sys.platform == "win32":
            self.tw_cw.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        window.setCentralWidget(self.tw_cw)
        self.menu_bar = window.menuBar()

        # ========== Menu Bar =====================
        self.menu_browsers = self.menu_bar.addMenu("浏览器")
        self.act_browser_chrome = QtGui.QAction(icons["chrome"], "Chrome", window)
        self.act_browser_edge = QtGui.QAction(icons["edge"], "Edge", window)
        self.act_browser_brave = QtGui.QAction(icons["brave"], "Brave", window)
        self.act_browser_chrome.setCheckable(True)
        # 保证子窗口的初始化成功
        self.act_browser_chrome.setChecked(True)
        self.act_browser_edge.setCheckable(True)
        self.act_browser_brave.setCheckable(True)
        self.acg_browsers = QtGui.QActionGroup(window)
        self.acg_browsers.setExclusive(True)
        self.acg_browsers.addAction(self.act_browser_chrome)
        self.acg_browsers.addAction(self.act_browser_edge)
        self.acg_browsers.addAction(self.act_browser_brave)
        self.menu_browsers.addActions([self.act_browser_chrome,
                                       self.act_browser_edge,
                                       self.act_browser_brave])

        self.menu_help = self.menu_bar.addMenu("帮助")
        self.act_settings = QtGui.QAction("偏好设置", window)
        self.act_clear_log = QtGui.QAction("清空日志", window)
        self.act_about = QtGui.QAction("关于", window)
        self.act_about_qt = QtGui.QAction("关于 Qt", window)
        self.menu_help.addAction(self.act_settings)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.act_clear_log)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.act_about)
        self.menu_help.addAction(self.act_about_qt)

        # =============== Central Widget ==============
        browser = self.acg_browsers.checkedAction().text()
        self.wg_check_plugins = CheckPluginsWin(browser, self.tw_cw)
        self.tw_cw.addTab(self.wg_check_plugins, icons["bpc"], "插件")
        self.wg_check_bookmarks = CheckBookmarksWin(browser, self.tw_cw)
        self.tw_cw.addTab(self.wg_check_bookmarks, icons["bmc"], "书签")
        self.wg_check_settings = CheckSettingsWin(browser, self.tw_cw)
        self.tw_cw.addTab(self.wg_check_settings, icons["bsc"], "设置")


class ChromHelperMainWin(QtWidgets.QMainWindow):

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, org_name: str, app_name: str, version: list[int]):
        super().__init__(parent)
        self.version = version
        self.org_name = org_name
        self.app_name = app_name
        self.ui = UiChromHelperMainWin(self)

        # ====== Menu Bar =========
        self.ui.act_settings.triggered.connect(self.on_act_settings_triggered)
        self.ui.act_clear_log.triggered.connect(self.on_act_clear_log_triggered)
        self.ui.act_about.triggered.connect(self.on_act_about_triggered)
        self.ui.act_about_qt.triggered.connect(self.on_act_about_qt_triggered)
        self.ui.acg_browsers.triggered.connect(self.on_acg_browsers_triggered)

        # 为了触发槽函数
        self.ui.act_browser_chrome.trigger()

    def on_acg_browsers_triggered(self, action: QtGui.QAction):
        browser = action.text()
        self.ui.wg_check_plugins.on_browser_changed(browser)
        self.ui.wg_check_bookmarks.on_browser_changed(browser)
        self.ui.wg_check_settings.on_browser_changed(browser)

    def on_act_settings_triggered(self):
        cs_win = ChromSettingsWin(self)
        cs_win.exec()

    def on_act_clear_log_triggered(self):
        log_dir = get_log_dir(sys.platform)
        if log_dir is None:
            return
        app_log_dir = Path(log_dir, self.org_name, self.app_name)
        if not app_log_dir.exists():
            return
        shutil.rmtree(app_log_dir, ignore_errors=True)

    def on_act_about_triggered(self):
        version = self.version
        about_text = ("Chromium 核心浏览器辅助工具\n\n旨在更方便地对以 Chromium 为核心的浏览器"
                      "进行快速设置、插件检查、书签检查、书签导出等操作。\n\n"
                      f"当前版本：v{version[0]}.{version[1]}.{version[2]}，发布日期：{version[-1]}")
        QtWidgets.QMessageBox.about(self, "关于", about_text)

    def on_act_about_qt_triggered(self):
        QtWidgets.QMessageBox.aboutQt(self, "关于 Qt")


def launch(org_name: str, app_name: str, has_log: bool, log_err: str, version: list[int]):
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(org_name)
    app.setApplicationName(app_name)

    win = ChromHelperMainWin(org_name=org_name, app_name=app_name, version=version)
    win.show()
    if not has_log:
        QtWidgets.QMessageBox.information(win, "提示", f"日志记录未开启：{log_err}")
    return app.exec()
