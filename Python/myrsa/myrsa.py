# code: utf8
import sys
import time
from pathlib import Path
from enum import IntEnum, unique
from PySide6 import QtWidgets, QtCore, QtGui

from easy import gen_new_keys, encrypt_file, decrypt_file

import myrsa_rc


version = (1, 0, 20230709)

translate = QtCore.QCoreApplication.translate


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(640, 258)
        window.setWindowIcon(QtGui.QIcon(":/myrsa16.ico"))

        self.gbx_gen = QtWidgets.QGroupBox(window)
        self.vly_gbx_gen = QtWidgets.QVBoxLayout()

        self.hly_new_key_path = QtWidgets.QHBoxLayout()
        self.lne_new_key_path = QtWidgets.QLineEdit(self.gbx_gen)

        self.pbn_new_key_path = QtWidgets.QPushButton(self.gbx_gen)
        self.hly_new_key_path.addWidget(self.lne_new_key_path)
        self.hly_new_key_path.addWidget(self.pbn_new_key_path)

        self.hly_gen_set = QtWidgets.QHBoxLayout()
        self.lb_new_key_name = QtWidgets.QLabel(self.gbx_gen)
        self.lne_new_key_name = QtWidgets.QLineEdit("key", self.gbx_gen)
        self.lb_key_bits = QtWidgets.QLabel(self.gbx_gen)
        self.cmbx_bits = QtWidgets.QComboBox(self.gbx_gen)
        self.cmbx_bits.addItems(["2048", "1024", "512", "256"])
        self.cmbx_bits.setCurrentIndex(1)
        self.pbn_gen = QtWidgets.QPushButton(self.gbx_gen)

        self.lb_gen_state = QtWidgets.QLabel(self.gbx_gen)
        self.lb_gen_state.setVisible(False)
        self.lb_gen_state.setFrameShape(QtWidgets.QLabel.Shape.Box)
        self.lb_gen_state.setFrameShadow(QtWidgets.QLabel.Shadow.Sunken)

        self.hly_gen_set.addWidget(self.lb_new_key_name)
        self.hly_gen_set.addWidget(self.lne_new_key_name)
        self.hly_gen_set.addWidget(self.lb_key_bits)
        self.hly_gen_set.addWidget(self.cmbx_bits)
        self.hly_gen_set.addStretch(1)
        self.hly_gen_set.addWidget(self.pbn_gen)

        self.vly_gbx_gen.addLayout(self.hly_new_key_path)
        self.vly_gbx_gen.addLayout(self.hly_gen_set)
        self.vly_gbx_gen.addWidget(self.lb_gen_state)
        self.gbx_gen.setLayout(self.vly_gbx_gen)

        self.gbx_run = QtWidgets.QGroupBox(window)
        self.gly_gbx_run = QtWidgets.QGridLayout()
        self.lne_key_path = QtWidgets.QLineEdit(self.gbx_run)
        self.lne_file_path = QtWidgets.QLineEdit(self.gbx_run)
        self.lne_save_path = QtWidgets.QLineEdit(self.gbx_run)
        self.pbn_key_path = QtWidgets.QPushButton(self.gbx_run)
        self.pbn_file_path = QtWidgets.QPushButton(self.gbx_run)
        self.pbn_save_path = QtWidgets.QPushButton(self.gbx_run)

        self.vly_run_right = QtWidgets.QVBoxLayout()
        self.bgp_enc_dec = QtWidgets.QButtonGroup(self.gbx_run)
        self.rbn_enc = QtWidgets.QRadioButton(self.gbx_run)
        self.rbn_dec = QtWidgets.QRadioButton(self.gbx_run)
        self.bgp_enc_dec.addButton(self.rbn_enc, 0)
        self.bgp_enc_dec.addButton(self.rbn_dec, 1)
        self.pbn_run = QtWidgets.QPushButton(self.gbx_run)
        self.vly_run_right.addWidget(self.rbn_enc)
        self.vly_run_right.addWidget(self.rbn_dec)
        self.vly_run_right.addWidget(self.pbn_run)
        self.pgb_run = QtWidgets.QProgressBar(self.gbx_run)
        self.pgb_run.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lb_run_state = QtWidgets.QLabel(self.gbx_run)
        self.lb_run_state.setVisible(False)
        self.lb_run_state.setFrameShape(QtWidgets.QLabel.Shape.Box)
        self.lb_run_state.setFrameShadow(QtWidgets.QLabel.Shadow.Sunken)

        self.gly_gbx_run.addWidget(self.lne_key_path, 0, 0)
        self.gly_gbx_run.addWidget(self.lne_file_path, 1, 0)
        self.gly_gbx_run.addWidget(self.lne_save_path, 2, 0)
        self.gly_gbx_run.addWidget(self.pbn_key_path, 0, 1)
        self.gly_gbx_run.addWidget(self.pbn_file_path, 1, 1)
        self.gly_gbx_run.addWidget(self.pbn_save_path, 2, 1)
        self.gly_gbx_run.addLayout(self.vly_run_right, 0, 2, 3, 1)
        self.gly_gbx_run.addWidget(self.pgb_run, 3, 0, 1, 3)
        self.gly_gbx_run.addWidget(self.lb_run_state, 4, 0, 1, 3)
        self.gbx_run.setLayout(self.gly_gbx_run)

        self.hly_bot = QtWidgets.QHBoxLayout()
        self.lb_version = QtWidgets.QLabel(window)
        self.cmbx_lang = QtWidgets.QComboBox(window)
        self.cmbx_lang.addItems(["English", "简体中文"])
        self.hly_bot.addWidget(self.lb_version)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.cmbx_lang)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.vly_m.addWidget(self.gbx_gen)
        self.vly_m.addStretch(1)
        self.vly_m.addWidget(self.gbx_run)
        self.vly_m.addLayout(self.hly_bot)

        window.setLayout(self.vly_m)
        self.re_translate(window)

    def re_translate(self, window: QtWidgets.QWidget):
        window.setWindowTitle(translate("MainWin", "My RSA"))

        self.gbx_gen.setTitle(translate("MainWin", "Generate New Keys"))
        self.lne_new_key_path.setPlaceholderText(translate("MainWin", "The path to save the new keys"))
        self.pbn_new_key_path.setText(translate("MainWin", "Browse"))
        self.lb_new_key_name.setText(translate("MainWin", "Key name:"))
        self.lb_key_bits.setText(translate("MainWin", "Key bits:"))
        self.pbn_gen.setText(translate("MainWin", "Generate"))

        self.gbx_run.setTitle(translate("MainWin", "Encrypt and Decrypt"))
        self.lne_key_path.setPlaceholderText(translate("MainWin", "The path of the key file"))
        self.lne_file_path.setPlaceholderText(translate("MainWin", "The path of the file to operate"))
        self.lne_save_path.setPlaceholderText(translate("MainWin", "The path to save the new file"))
        self.pbn_key_path.setText(translate("MainWin", "Browse"))
        self.pbn_file_path.setText(translate("MainWin", "Browse"))
        self.pbn_save_path.setText(translate("MainWin", "Browse"))
        self.rbn_enc.setText(translate("MainWin", "Encrypt"))
        self.rbn_dec.setText(translate("MainWin", "Decrypt"))
        self.pbn_run.setText(translate("MainWin", "Run"))

        self.lb_version.setText(translate("MainWin", "Version: v{0}.{1}, Date: {2}").format(
            version[0], version[1], version[-1]
        ))


@unique
class _WidgetFlag(IntEnum):
    lb_gen_state = 1
    lb_run_state = 2


@unique
class _ContentFlag(IntEnum):
    path_invalid = 1
    path_empty = 2
    new_key_exist = 3
    key_gen_start = 4
    key_gen_success = 5
    run_without_op = 6
    keyfile_invalid = 7
    encrypt_start = 8
    write_file = 9
    encrypt_success = 10
    encfile_invalid = 11
    decrypt_start = 12
    decrypt_success = 13


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)
        self.current_tr = None  # type: QtCore.QTranslator | None
        self.tr_zh_cn = QtCore.QTranslator()
        self.tr_zh_cn.load(":/translations/myrsa_zh_cn.qm")

        self._widget_current_content = {}

        self.ui.pbn_new_key_path.clicked.connect(self.on_pbn_new_key_path_clicked)
        self.ui.pbn_gen.clicked.connect(self.on_pbn_gen_clicked)
        self.ui.cmbx_lang.currentIndexChanged.connect(self.on_cmbx_lang_current_index_changed)

        self.ui.pbn_run.clicked.connect(self.on_pbn_run_clicked)
        self.ui.bgp_enc_dec.idClicked.connect(self.on_bgp_enc_dec_id_clicked)
        self.ui.pbn_key_path.clicked.connect(self.on_pbn_key_path_clicked)
        self.ui.pbn_file_path.clicked.connect(self.on_pbn_file_path_clicked)
        self.ui.pbn_save_path.clicked.connect(self.on_pbn_save_path_clicked)

    def on_cmbx_lang_current_index_changed(self, index: int):
        if self.current_tr is not None:
            QtCore.QCoreApplication.removeTranslator(self.current_tr)

        if index == 1:
            self.current_tr = self.tr_zh_cn
        else:
            self.current_tr = None

        if self.current_tr is not None:
            QtCore.QCoreApplication.installTranslator(self.current_tr)

        self.ui.re_translate(self)
        for wf, (cf, args) in self._widget_current_content.items():
            self._dynamic_re_translate(wf, cf, *args, ch_lang=True)

    def _dynamic_re_translate(self, wf: _WidgetFlag, cf: _ContentFlag, *args, ch_lang=False):
        if wf == _WidgetFlag.lb_gen_state:
            if cf == _ContentFlag.path_invalid:
                self.ui.lb_gen_state.setText(translate("MainWin", "The path does not exist or is not a directory."))
            elif cf == _ContentFlag.new_key_exist:
                self.ui.lb_gen_state.setText(translate("MainWin", "The file [{0}] already exists.").format(*args))
            elif cf == _ContentFlag.key_gen_success:
                self.ui.lb_gen_state.setText(
                    translate("MainWin", "Successfully generated new keys. Time: {0}s.").format(*args))
            elif cf == _ContentFlag.path_empty:
                self.ui.lb_gen_state.setText(translate("MainWin", "The path is empty."))
            elif cf == _ContentFlag.key_gen_start:
                self.ui.lb_gen_state.setText(translate("MainWin", "Start generating new keys..."))
        elif wf == _WidgetFlag.lb_run_state:
            if cf == _ContentFlag.path_empty:
                self.ui.lb_run_state.setText(translate("MainWin", "Please fill out all file paths before running."))
            elif cf == _ContentFlag.path_invalid:
                self.ui.lb_run_state.setText(
                    translate("MainWin", "At least one of the file paths is invalid. Please check again."))
            elif cf == _ContentFlag.run_without_op:
                self.ui.lb_run_state.setText(translate("MainWin", "Please select the operation you want to perform."))
            elif cf == _ContentFlag.keyfile_invalid:
                self.ui.lb_run_state.setText(translate("MainWin", "Not a valid key file."))
            elif cf == _ContentFlag.encrypt_start:
                self.ui.lb_run_state.setText(translate("MainWin", "Start encrypting..."))
            elif cf == _ContentFlag.write_file:
                self.ui.lb_run_state.setText(translate("MainWin", "Writing to file..."))
            elif cf == _ContentFlag.encrypt_success:
                self.ui.lb_run_state.setText(
                    translate("MainWin", "Successfully encrypted the file. Time: {0}s.").format(*args))
            elif cf == _ContentFlag.encfile_invalid:
                self.ui.lb_run_state.setText(translate("MainWin", "Not an encrypted file."))
            elif cf == _ContentFlag.decrypt_start:
                self.ui.lb_run_state.setText(translate("MainWin", "Start decrypting..."))
            elif cf == _ContentFlag.decrypt_success:
                self.ui.lb_run_state.setText(
                    translate("MainWin", "Successfully decrypted the file. Time: {0}s.").format(*args))

        if ch_lang is False:
            self._widget_current_content[wf] = (cf, args)

    @staticmethod
    def _change_window_text_to(widget: QtWidgets.QWidget, color: str | QtGui.QColor):
        palette = widget.palette()
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, color)
        widget.setPalette(palette)

    def _accept_file_exist_warning(self):
        if Path(self.ui.lne_save_path.text()).is_file():
            b = QtWidgets.QMessageBox.question(
                self, translate("MainWin", "Warning"),
                translate("MainWin", "The file to save already exists. Continue to overwrite?"))
            if b == QtWidgets.QMessageBox.StandardButton.No:
                return True
        return False

    def on_pbn_gen_clicked(self):
        self.ui.lb_gen_state.setVisible(True)
        key_path_text = self.ui.lne_new_key_path.text()
        if len(key_path_text) == 0:
            self._change_window_text_to(self.ui.lb_gen_state, "red")
            self._dynamic_re_translate(_WidgetFlag.lb_gen_state, _ContentFlag.path_empty)
            return

        key_path = Path(key_path_text)
        if not (key_path.exists() and key_path.is_dir()):
            self._change_window_text_to(self.ui.lb_gen_state, "red")
            self._dynamic_re_translate(_WidgetFlag.lb_gen_state, _ContentFlag.path_invalid)
            return
        key_file_ext = [".pubk", ".pvtk"]
        key_name = self.ui.lne_new_key_name.text()
        key_files = {
            0: None, 1: None
        }
        for i, e in enumerate(key_file_ext):
            key = f"{key_name}{e}"
            key_files[i] = key_file = Path(key_path, key)
            if key_file.exists():
                self._change_window_text_to(self.ui.lb_gen_state, "red")
                self._dynamic_re_translate(_WidgetFlag.lb_gen_state, _ContentFlag.new_key_exist, key)
                return

        self._change_window_text_to(self.ui.lb_gen_state, "blue")
        st = time.time()
        for i in gen_new_keys(int(self.ui.cmbx_bits.currentText()), key_files[0], key_files[1]):
            if i == 1:
                self._dynamic_re_translate(_WidgetFlag.lb_gen_state, _ContentFlag.key_gen_start)
            elif i == 2:
                self._dynamic_re_translate(_WidgetFlag.lb_gen_state, _ContentFlag.key_gen_success,
                                           f"{time.time() - st:.2f}")

    def on_pbn_new_key_path_clicked(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, translate("MainWin", "Browse"))
        if len(dirname) == 0:
            return
        self.ui.lne_new_key_path.setText(dirname)

    def on_bgp_enc_dec_id_clicked(self, id: int):
        filepath = self.ui.lne_file_path.text()
        if len(filepath) == 0:
            return

        filepath_p = Path(filepath)
        filename = filepath_p.name

        savepath = self.ui.lne_save_path.text()
        if len(savepath) == 0:
            dirname = filepath_p.parent
        else:
            savepath_p = Path(savepath)
            if savepath_p.is_dir():
                dirname = savepath_p
            elif savepath_p.parent.is_dir():
                dirname = savepath_p.parent
            else:
                dirname = filepath_p.parent

        if id == 0:

            self.ui.lne_save_path.setText(QtCore.QDir(f"{dirname}/{filename}.b").path())
        elif id == 1:
            if filename.endswith(".b"):
                self.ui.lne_save_path.setText(QtCore.QDir(f"{dirname}/{filename[:-2]}").path())
            else:
                self.ui.lne_save_path.setText(QtCore.QDir(f"{dirname}/d_{filename}").path())

    def on_pbn_key_path_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, translate("MainWin", "Browse"))
        if len(filename) == 0:
            return
        self.ui.lne_key_path.setText(filename)

    def on_pbn_file_path_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, translate("MainWin", "Browse"))
        if len(filename) == 0:
            return
        self.ui.lne_file_path.setText(filename)

    def on_pbn_save_path_clicked(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, translate("MainWin", "Browse"))
        if len(dirname) == 0:
            return
        self.ui.lne_save_path.setText(dirname)
        self.ui.bgp_enc_dec.setExclusive(False)
        self.ui.rbn_enc.setChecked(False)
        self.ui.rbn_dec.setChecked(False)
        self.ui.bgp_enc_dec.setExclusive(True)

    def on_pbn_run_clicked(self):
        self.ui.lb_run_state.setVisible(True)

        key_path = self.ui.lne_key_path.text()
        file_path = self.ui.lne_file_path.text()
        save_path = self.ui.lne_save_path.text()
        if not all((key_path, file_path, save_path)):
            self._change_window_text_to(self.ui.lb_run_state, "red")
            self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.path_empty)
            return

        key_path_p = Path(key_path)
        file_path_p = Path(file_path)
        save_path_p = Path(save_path)
        if not (key_path_p.is_file() and file_path_p.is_file() and save_path_p.parent.is_dir()):
            self._change_window_text_to(self.ui.lb_run_state, "red")
            self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.path_invalid)
            return

        if self.ui.bgp_enc_dec.checkedId() == -1:
            self._change_window_text_to(self.ui.lb_run_state, "red")
            self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.run_without_op)
            return

        if self._accept_file_exist_warning():
            return

        if self.ui.bgp_enc_dec.checkedId() == 0:
            st = time.time()
            for i in encrypt_file(key_path, file_path, save_path):
                if i == 1:
                    self._change_window_text_to(self.ui.lb_run_state, "red")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.keyfile_invalid)
                elif i == 2:
                    self._change_window_text_to(self.ui.lb_run_state, "blue")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.encrypt_start)
                elif i == 4:
                    self._change_window_text_to(self.ui.lb_run_state, "blue")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.write_file)
                elif i == 5:
                    self._change_window_text_to(self.ui.lb_run_state, "blue")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.encrypt_success,
                                               f"{time.time() - st:.2f}")
                elif isinstance(i, tuple):
                    self.ui.pgb_run.setValue(i[1])
        elif self.ui.bgp_enc_dec.checkedId() == 1:
            st = time.time()
            for i in decrypt_file(key_path, file_path, save_path):
                if i == 1:
                    self._change_window_text_to(self.ui.lb_run_state, "red")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.keyfile_invalid)
                elif i == 6:
                    self._change_window_text_to(self.ui.lb_run_state, "red")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.encfile_invalid)
                elif i == 2:
                    self._change_window_text_to(self.ui.lb_run_state, "blue")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.decrypt_start)
                elif i == 4:
                    self._change_window_text_to(self.ui.lb_run_state, "blue")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.write_file)
                elif i == 5:
                    self._change_window_text_to(self.ui.lb_run_state, "blue")
                    self._dynamic_re_translate(_WidgetFlag.lb_run_state, _ContentFlag.decrypt_success,
                                               f"{time.time() - st:.2f}")
                elif isinstance(i, tuple):
                    self.ui.pgb_run.setValue(i[1])


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
