# code: utf8

# Change Log:
#
# v1.0 图形界面版本
#
# v0.1 粗糙的命令行英文版本，能用
#

#########################################################################
#  ______                       _   ____  __  __ ___  _  _________   __ #
# |  ____|                     | | |  _ \|  \/  |__ \| |/ /  __ \ \ / / #
# | |__  __  ___ __   ___  _ __| |_| |_) | \  / |  ) | ' /| |__) \ V /  #
# |  __| \ \/ / '_ \ / _ \| '__| __|  _ <| |\/| | / /|  < |  ___/ > <   #
# | |____ >  <| |_) | (_) | |  | |_| |_) | |  | |/ /_| . \| |    / . \  #
# |______/_/\_\ .__/ \___/|_|   \__|____/|_|  |_|____|_|\_\_|   /_/ \_\ #
#             | |                                                       #
#             |_|                                                       #
#########################################################################

import os
import sys
from pathlib import Path

from PySide6 import QtWidgets, QtCore, QtGui
from bm2kps import bm2xml

import ebk_rc

version = [1, 0, 20230725]

_BROWSERS = ["Chrome", "Edge", "Brave"]


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(480, 360)
        window.setWindowTitle("导出书签到 KeePassXC")
        window.setWindowIcon(QtGui.QIcon(":/img/ebk_16.png"))

        self.icon_eye = QtGui.QIcon(":/img/eye.svg")
        self.icon_eye_off = QtGui.QIcon(":/img/eye-off.svg")
        self.icon_ellipsis = QtGui.QIcon(":/img/ellipsis.svg")

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.gbx_config = QtWidgets.QGroupBox("配置", window)
        self.vly_m.addWidget(self.gbx_config)

        self.vly_gbx_config = QtWidgets.QVBoxLayout()
        self.gbx_config.setLayout(self.vly_gbx_config)

        self.hly_top_gbx_config = QtWidgets.QHBoxLayout()
        self.vly_gbx_config.addLayout(self.hly_top_gbx_config)

        self.lb_browser = QtWidgets.QLabel("切换浏览器：", self.gbx_config)
        self.cmbx_browser = QtWidgets.QComboBox(self.gbx_config)
        self.cmbx_browser.addItems(_BROWSERS)
        self.hly_top_gbx_config.addWidget(self.lb_browser)
        self.hly_top_gbx_config.addWidget(self.cmbx_browser)
        self.hly_top_gbx_config.addStretch(1)

        self.hln_top = QtWidgets.QFrame(self.gbx_config)
        self.hln_top.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.hln_top.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.vly_gbx_config.addWidget(self.hln_top)

        self.gly_mid_gbx_config = QtWidgets.QGridLayout()
        self.vly_gbx_config.addLayout(self.gly_mid_gbx_config)

        self.lb_pass = QtWidgets.QLabel("密　　码：", self.gbx_config)
        self.lne_pass = QtWidgets.QLineEdit(self.gbx_config)
        self.lne_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pbn_show_pass = QtWidgets.QPushButton(icon=self.icon_eye_off, parent=self.gbx_config)
        self.lb_kpx_path = QtWidgets.QLabel("输出路径：", self.gbx_config)
        self.lne_kpx_path = QtWidgets.QLineEdit(self.gbx_config)
        self.pbn_browse_kpx_path = QtWidgets.QPushButton(icon=self.icon_ellipsis, parent=self.gbx_config)
        self.lb_cli_path = QtWidgets.QLabel("执行路径：", self.gbx_config)
        self.lne_cli_path = QtWidgets.QLineEdit(self.gbx_config)
        self.pbn_browse_cli_path = QtWidgets.QPushButton(icon=self.icon_ellipsis, parent=self.gbx_config)
        self.gly_mid_gbx_config.addWidget(self.lb_pass, 0, 0)
        self.gly_mid_gbx_config.addWidget(self.lne_pass, 0, 1)
        self.gly_mid_gbx_config.addWidget(self.pbn_show_pass, 0, 2)
        self.gly_mid_gbx_config.addWidget(self.lb_kpx_path, 1, 0)
        self.gly_mid_gbx_config.addWidget(self.lne_kpx_path, 1, 1)
        self.gly_mid_gbx_config.addWidget(self.pbn_browse_kpx_path, 1, 2)
        self.gly_mid_gbx_config.addWidget(self.lb_cli_path, 2, 0)
        self.gly_mid_gbx_config.addWidget(self.lne_cli_path, 2, 1)
        self.gly_mid_gbx_config.addWidget(self.pbn_browse_cli_path, 2, 2)

        self.hln_mid = QtWidgets.QFrame(self.gbx_config)
        self.hln_mid.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.hln_mid.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.vly_gbx_config.addWidget(self.hln_mid)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.vly_gbx_config.addLayout(self.hly_bot)

        self.cbx_keep_xml = QtWidgets.QCheckBox("保留 XML 文件", self.gbx_config)
        self.cbx_clear_pass = QtWidgets.QCheckBox("导出后清空密码", self.gbx_config)
        self.cbx_clear_pass.setChecked(True)
        self.pbn_export = QtWidgets.QPushButton("导出", self.gbx_config)
        self.pbn_clear = QtWidgets.QPushButton("清空", self.gbx_config)
        self.hly_bot.addWidget(self.cbx_keep_xml)
        self.hly_bot.addWidget(self.cbx_clear_pass)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_export)
        self.hly_bot.addWidget(self.pbn_clear)

        self.txe_output = QtWidgets.QTextEdit(self.gbx_config)
        self.txe_output.setReadOnly(True)
        self.vly_gbx_config.addWidget(self.txe_output)


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)
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
        self._show_version()
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

    def _show_version(self):
        ver_info = f"版本：v{version[0]}.{version[1]}，日期：{version[-1]}"
        self.ui.txe_output.append(ver_info)

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
        browser = self.ui.cmbx_browser.currentText()
        password = self.ui.lne_pass.text()
        kpx_path = self.ui.lne_kpx_path.text()
        cli_path = self.ui.lne_cli_path.text()
        save_xml = self.ui.cbx_keep_xml.checkState() == QtCore.Qt.CheckState.Checked
        clear_pass = self.ui.cbx_clear_pass.checkState() == QtCore.Qt.CheckState.Checked

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
            arguments = ["import", "-p", f'"{xml_path}"', f'"{kpx_path}"']
        else:
            arguments = ["import", f'"{xml_path}"', f'"{kpx_path}"']

        match sys.platform:
            case "win32":
                self.prc_echo_pass.setProgram("powershell")
                self.prc_echo_pass.setNativeArguments(" ".join(["echo", f"{password},{password}"]))
                self.prc_kpx_import.setProgram(cli_path)
                self.prc_kpx_import.setNativeArguments(" ".join(arguments))
            case "darwin":
                self.prc_echo_pass.setProgram("echo")
                self.prc_echo_pass.setArguments(["-e", f"{password}\\n{password}"])
                self.prc_kpx_import.setProgram(cli_path)
                self.prc_kpx_import.setArguments(arguments)
            case _:
                QtWidgets.QMessageBox.critical(self, "错误", f"不支持的操作系统：{sys.platform}")
                return

        self.ui.txe_output.append("正在导出书签……")
        bm2xml(browser, xml_path)
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
        self.ui.txe_output.append("成功生成数据库文件。\n")


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
