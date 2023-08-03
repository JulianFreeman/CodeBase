# code: utf8
import os
import sys
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from jnlib.pyside6_utils import HorizontalLine

from bookmarks2kdbx import bm2xml


class UiExportBookmarksWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.icon_eye = QtGui.QIcon(":/img/svg/eye.svg")
        self.icon_eye_off = QtGui.QIcon(":/img/svg/eye-off.svg")
        self.icon_ellipsis = QtGui.QIcon(":/img/svg/ellipsis.svg")

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.gly_top = QtWidgets.QGridLayout()
        self.vly_m.addLayout(self.gly_top)

        self.lb_pass = QtWidgets.QLabel("密　　码：", window)
        self.lne_pass = QtWidgets.QLineEdit(window)
        self.lne_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pbn_show_pass = QtWidgets.QPushButton(icon=self.icon_eye_off, parent=window)
        self.lb_kpx_path = QtWidgets.QLabel("输出路径：", window)
        self.lne_kpx_path = QtWidgets.QLineEdit(window)
        self.pbn_browse_kpx_path = QtWidgets.QPushButton(icon=self.icon_ellipsis, parent=window)
        self.lb_cli_path = QtWidgets.QLabel("执行路径：", window)
        self.lne_cli_path = QtWidgets.QLineEdit(window)
        self.pbn_browse_cli_path = QtWidgets.QPushButton(icon=self.icon_ellipsis, parent=window)
        self.gly_top.addWidget(self.lb_pass, 0, 0)
        self.gly_top.addWidget(self.lne_pass, 0, 1)
        self.gly_top.addWidget(self.pbn_show_pass, 0, 2)
        self.gly_top.addWidget(self.lb_kpx_path, 1, 0)
        self.gly_top.addWidget(self.lne_kpx_path, 1, 1)
        self.gly_top.addWidget(self.pbn_browse_kpx_path, 1, 2)
        self.gly_top.addWidget(self.lb_cli_path, 2, 0)
        self.gly_top.addWidget(self.lne_cli_path, 2, 1)
        self.gly_top.addWidget(self.pbn_browse_cli_path, 2, 2)

        self.hln_mid = HorizontalLine(window)
        self.vly_m.addWidget(self.hln_mid)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_bot)

        self.cbx_google_only = QtWidgets.QCheckBox("仅导出谷歌网盘链接", window)
        self.cbx_google_only.setChecked(True)
        self.cbx_keep_xml = QtWidgets.QCheckBox("保留 XML 文件", window)
        self.cbx_clear_pass = QtWidgets.QCheckBox("导出后清空密码", window)
        self.cbx_clear_pass.setChecked(True)
        self.pbn_export = QtWidgets.QPushButton("导出", window)
        self.pbn_clear = QtWidgets.QPushButton("清空", window)
        self.hly_bot.addWidget(self.cbx_google_only)
        self.hly_bot.addWidget(self.cbx_keep_xml)
        self.hly_bot.addWidget(self.cbx_clear_pass)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_export)
        self.hly_bot.addWidget(self.pbn_clear)

        self.txe_output = QtWidgets.QTextEdit(window)
        self.txe_output.setReadOnly(True)
        self.vly_m.addWidget(self.txe_output)


class ExportBookmarksWin(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.browser = browser
        self.ui = UiExportBookmarksWin(self)
        self._kpx_ver = ()
        self.prc_kpx_ver = QtCore.QProcess(self)
        self.prc_kpx_ver.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)

        self.prc_echo_pass = QtCore.QProcess(self)
        self.prc_kpx_import = QtCore.QProcess(self)
        self.prc_echo_pass.setStandardOutputProcess(self.prc_kpx_import)
        self.prc_kpx_import.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)

        self.prc_kpx_ver.readyReadStandardOutput.connect(self.on_prc_kpx_ver_ready_read_standard_output)
        self.prc_kpx_import.finished.connect(self.on_prc_kpx_import_finished)

        self._get_kpx_cli()
        self._show_kpx_version()

        self.ui.lne_cli_path.textChanged.connect(self.on_lne_cli_path_text_changed)
        self.ui.pbn_browse_cli_path.clicked.connect(self.on_pbn_browse_cli_path_clicked)
        self.ui.pbn_browse_kpx_path.clicked.connect(self.on_pbn_browse_kpx_path_clicked)
        self.ui.pbn_show_pass.clicked.connect(self.on_pbn_show_pass_clicked)
        self.ui.pbn_export.clicked.connect(self.on_pbn_export_clicked)
        self.ui.pbn_clear.clicked.connect(lambda: self.ui.txe_output.clear())

    def _get_kpx_cli(self):
        plat = sys.platform
        default_kps_cli_path = {
            "win32": r"C:\Program Files\KeePassXC\keepassxc-cli.exe",
            "darwin": r"/Applications/KeePassXC.app/Contents/MacOS/keepassxc-cli"
        }
        cli_path = default_kps_cli_path.get(plat, None)
        if cli_path is not None and Path(cli_path).exists():
            self.ui.lne_cli_path.setText(cli_path)

    def _show_kpx_version(self, cli_path: str = None):
        if cli_path is None:
            cli_path = self.ui.lne_cli_path.text()
        cli_path_p = Path(cli_path)

        if len(cli_path) == 0 or not cli_path_p.exists():
            self.ui.txe_output.append("没有找到 keepassxc_cli 文件，请指定正确的执行路径。")
            return

        self.prc_kpx_ver.setProgram(cli_path)
        self.prc_kpx_ver.setArguments(["--version"])
        self.prc_kpx_ver.start()

    def on_browser_changed(self, browser: str):
        self.browser = browser

    def on_lne_cli_path_text_changed(self, text):
        self._show_kpx_version(text)

    def on_prc_kpx_ver_ready_read_standard_output(self):
        ver = self.prc_kpx_ver.readAllStandardOutput().data().decode("utf8")
        self.ui.txe_output.append(f"KeePassXC 版本：{ver}")
        self._kpx_ver = tuple([int(v) for v in ver.split(".")])

    def on_pbn_browse_cli_path_clicked(self):
        cli_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "执行路径", filter="所有文件(*)")
        if len(cli_path) == 0:
            return
        self.ui.lne_cli_path.setText(cli_path)

    def on_pbn_browse_kpx_path_clicked(self):
        kpx_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "输出路径", filter="KeePass 2 数据库 (*.kdbx);;所有文件(*)")
        if len(kpx_path) == 0:
            return
        self.ui.lne_kpx_path.setText(kpx_path)

    def on_pbn_show_pass_clicked(self):
        is_pass_mode = self.ui.lne_pass.echoMode() == QtWidgets.QLineEdit.EchoMode.Password
        if is_pass_mode:
            self.ui.lne_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.ui.pbn_show_pass.setIcon(self.ui.icon_eye)
        else:
            self.ui.lne_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.ui.pbn_show_pass.setIcon(self.ui.icon_eye_off)

    def on_pbn_export_clicked(self):
        browser = self.browser
        password = self.ui.lne_pass.text()
        kpx_path = self.ui.lne_kpx_path.text()
        cli_path = self.ui.lne_cli_path.text()
        save_xml = self.ui.cbx_keep_xml.checkState() == QtCore.Qt.CheckState.Checked
        clear_pass = self.ui.cbx_clear_pass.checkState() == QtCore.Qt.CheckState.Checked
        google_only = self.ui.cbx_google_only.checkState() == QtCore.Qt.CheckState.Checked

        if len(password) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有指定 KeePass 数据库密码。")
            return
        if len(kpx_path) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有指定输出文件路径。")
            return
        elif Path(kpx_path).exists():
            QtWidgets.QMessageBox.warning(self, "警告", "指定的输出文件已存在。")
            return
        if len(cli_path) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有指定 keepassxc_cli 执行文件路径。")
            return
        elif not Path(cli_path).exists():
            QtWidgets.QMessageBox.critical(self, "错误", "keepassxc_cli 执行文件不存在。")
            return

        xml_path = kpx_path + ".xml"
        if self._kpx_ver >= (2, 7, 0):
            arguments = ["import", "-p", xml_path, kpx_path]
        else:
            arguments = ["import", xml_path, kpx_path]

        match sys.platform:
            case "win32":
                self.prc_echo_pass.setProgram("powershell")
                self.prc_echo_pass.setArguments(["echo", f"{password},{password}"])
            case "darwin":
                self.prc_echo_pass.setProgram("bash")
                self.prc_echo_pass.setArguments(["-c", f'echo -e "{password}\\n{password}"'])
            case _:
                QtWidgets.QMessageBox.critical(self, "错误", f"不支持的操作系统：{sys.platform}")
                return
        self.prc_kpx_import.setProgram(cli_path)
        self.prc_kpx_import.setArguments(arguments)

        self.ui.txe_output.append("正在导出书签……")
        bm2xml(browser, xml_path, google_only)
        self.ui.txe_output.append("正在生成数据库文件……")
        self.prc_echo_pass.start()
        self.prc_kpx_import.start()

        self.prc_kpx_import.waitForFinished()

        if not save_xml:
            os.remove(xml_path)

        if clear_pass:
            self.ui.lne_pass.clear()

    def on_prc_kpx_import_finished(self):
        out = self.prc_kpx_import.readAllStandardOutput().data().decode("utf8")
        self.ui.txe_output.append(out)
        self.ui.txe_output.append("结束。\n")
