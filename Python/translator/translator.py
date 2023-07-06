# code: utf8

# Change log
#
# v1.1
# 1. 添加图标文件
# 2. 优化删除操作
#
# v1.0
# 初始版本
#

####################################################
#  _______                  _       _              #
# |__   __|                | |     | |             #
#    | |_ __ __ _ _ __  ___| | __ _| |_ ___  _ __  #
#    | | '__/ _` | '_ \/ __| |/ _` | __/ _ \| '__| #
#    | | | | (_| | | | \__ \ | (_| | || (_) | |    #
#    |_|_|  \__,_|_| |_|___/_|\__,_|\__\___/|_|    #
####################################################

import json
import sys
from PySide6 import QtWidgets, QtGui

import icons

version = (1, 1, 20230705)


class DebugWin(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.resize(640, 360)
        self.setWindowTitle("Debug")

        self.vly_m = QtWidgets.QVBoxLayout()
        self.txe_out = QtWidgets.QTextEdit(self)
        self.vly_m.addWidget(self.txe_out)

        self.setLayout(self.vly_m)

    def set_output(self, text: str):
        self.txe_out.setPlainText(text)


class AddRowsWin(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.resize(640, 180)
        self.setWindowTitle("Add Keys")

        self.vly_m = QtWidgets.QVBoxLayout()
        self.txe_keys = QtWidgets.QTextEdit(self)

        self.hly_buttons = QtWidgets.QHBoxLayout()
        self.dbbx_buttons = QtWidgets.QDialogButtonBox(self)
        self.dbbx_buttons.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.hly_buttons.addStretch(1)
        self.hly_buttons.addWidget(self.dbbx_buttons)

        self.vly_m.addWidget(self.txe_keys)
        self.vly_m.addLayout(self.hly_buttons)

        self.setLayout(self.vly_m)

        self.dbbx_buttons.accepted.connect(self.accept)
        self.dbbx_buttons.rejected.connect(self.reject)


class UiMainWin(object):
    def __init__(self, window: QtWidgets.QWidget):
        window.resize(800, 600)
        window.setWindowTitle("Translator Editor")
        window.setWindowIcon(QtGui.QIcon(":/translator16.ico"))

        self.hly_file_op = QtWidgets.QHBoxLayout()
        self.pbn_new = QtWidgets.QPushButton("New", window)
        self.pbn_open = QtWidgets.QPushButton("Open", window)
        self.pbn_save = QtWidgets.QPushButton("Save", window)
        self.pbn_save_as = QtWidgets.QPushButton("Save As", window)
        self.pbn_exit = QtWidgets.QPushButton("Exit", window)
        self.hly_file_op.addWidget(self.pbn_new)
        self.hly_file_op.addWidget(self.pbn_open)
        self.hly_file_op.addWidget(self.pbn_save)
        self.hly_file_op.addWidget(self.pbn_save_as)
        self.hly_file_op.addStretch(1)
        self.hly_file_op.addWidget(self.pbn_exit)

        self.hly_data_op = QtWidgets.QHBoxLayout()
        self.pbn_add = QtWidgets.QPushButton("Add", window)
        self.pbn_delete = QtWidgets.QPushButton("Delete", window)
        self.lne_locale = QtWidgets.QLineEdit("zh_cn", window)
        self.pbn_search = QtWidgets.QPushButton("Search", window)
        self.hly_data_op.addWidget(self.pbn_add)
        self.hly_data_op.addWidget(self.pbn_delete)
        self.hly_data_op.addStretch(1)
        self.hly_data_op.addWidget(self.lne_locale)
        self.hly_data_op.addWidget(self.pbn_search)

        self.tbw_words = QtWidgets.QTableWidget(window)
        self.tbw_words.setColumnCount(2)
        self.tbw_words.setHorizontalHeaderLabels(["Key", "Translation"])
        self.tbw_words.horizontalHeader().setStretchLastSection(True)

        self.hly_bot = QtWidgets.QHBoxLayout()

        self.lb_state = QtWidgets.QLabel(window)
        self.pbn_debug = QtWidgets.QPushButton("Debug", window)

        self.hly_bot.addWidget(self.lb_state)
        self.hly_bot.addStretch(1)
        self.hly_bot.addWidget(self.pbn_debug)

        self.vly_m = QtWidgets.QVBoxLayout()
        self.vly_m.addLayout(self.hly_file_op)
        self.vly_m.addLayout(self.hly_data_op)
        self.vly_m.addWidget(self.tbw_words)
        self.vly_m.addLayout(self.hly_bot)

        window.setLayout(self.vly_m)


class MainWin(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)

        self._locale = ""
        self._dictionary = {}  # type: dict[str, dict[str, str]]
        self._current_file = ""
        self._on_read_lock = False
        self._row_keys_map = {}  # type: dict[int, str]

        self.ui.tbw_words.itemChanged.connect(self.on_tbw_words_item_changed)
        self.ui.pbn_new.clicked.connect(self.on_pbn_new_clicked)
        self.ui.pbn_open.clicked.connect(self.on_pbn_open_clicked)
        self.ui.pbn_save.clicked.connect(self.on_pbn_save_clicked)
        self.ui.pbn_save_as.clicked.connect(self.on_pbn_save_as_clicked)
        self.ui.pbn_exit.clicked.connect(self.on_pbn_exit_clicked)
        self.ui.pbn_search.clicked.connect(self.on_pbn_search_clicked)
        self.ui.pbn_debug.clicked.connect(self.on_pbn_debug_clicked)
        self.ui.pbn_add.clicked.connect(self.on_pbn_add_clicked)
        self.ui.pbn_delete.clicked.connect(self.on_pbn_delete_clicked)

    def _accept_unsaved_warning(self):
        if self.windowTitle().startswith("*"):
            b = QtWidgets.QMessageBox.question(
                self, "Warning",
                "It seems the current file has not been saved yet.\nAre you sure to continue?")
            if b == QtWidgets.QMessageBox.StandardButton.No:
                return True
        return False

    def _file_saved(self):
        if self.windowTitle().startswith("*"):
            self.setWindowTitle(self.windowTitle()[1:])

    def _file_changed(self):
        if not self.windowTitle().startswith("*"):
            self.setWindowTitle(f"*{self.windowTitle()}")

    def _read_dict(self) -> int:
        self._on_read_lock = True

        self._locale = self.ui.lne_locale.text()
        loc_dict = {key: self._dictionary[key].get(self._locale, "") for key in self._dictionary}
        ln_loc_dict = len(loc_dict)

        self.ui.tbw_words.clearContents()
        self.ui.tbw_words.setRowCount(ln_loc_dict)

        self._row_keys_map.clear()
        for i, key in enumerate(loc_dict):
            self._row_keys_map[i] = key

            key_item = QtWidgets.QTableWidgetItem(key)
            self.ui.tbw_words.setItem(i, 0, key_item)
            trn_item = QtWidgets.QTableWidgetItem(loc_dict[key])
            self.ui.tbw_words.setItem(i, 1, trn_item)

        self._on_read_lock = False
        return ln_loc_dict

    def on_tbw_words_item_changed(self, item: QtWidgets.QTableWidgetItem):
        if self._on_read_lock:
            return
        r, c, cur = item.row(), item.column(), item.text()
        prev = self._row_keys_map[r]

        if c == 0:
            self._row_keys_map[r] = cur
            self._dictionary[cur] = self._dictionary[prev]
            self._dictionary.pop(prev)
        else:
            self._dictionary[prev][self._locale] = cur

        self.ui.lb_state.setText(f"Updated row {r} column {c}")
        self._file_changed()

    def on_pbn_new_clicked(self):
        if self._accept_unsaved_warning():
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "New")
        if len(filename) == 0:
            return

        self._current_file = filename
        self._dictionary.clear()
        self._row_keys_map.clear()

        self.ui.tbw_words.clearContents()
        self.ui.tbw_words.setRowCount(0)

        self._file_changed()
        self.ui.lb_state.setText(f"New file [{filename}]")

    def on_pbn_open_clicked(self):
        if self._accept_unsaved_warning():
            return

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open")
        if len(filename) == 0:
            return
        try:
            with open(filename, "r", encoding="utf8") as fd:
                self._dictionary = json.load(fd)  # type: dict[str, dict[str, str]]
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.ui.lb_state.setText(f"Failed to load [{filename}]")
            return
        else:
            self.ui.lb_state.setText(f"Loaded [{filename}]")
        self._current_file = filename

        num_lines = self._read_dict()

        self.ui.lb_state.setText(f"{self.ui.lb_state.text()}\nInserted {num_lines} lines.")
        # to remove the possible *
        self._file_saved()

    def on_pbn_save_clicked(self):
        filename = self._current_file
        try:
            with open(filename, "w", encoding="utf8") as fd:
                json.dump(self._dictionary, fd, indent=4, ensure_ascii=False)
        except FileNotFoundError:
            self.ui.lb_state.setText("Failed to save. Cannot find the current file.")
            return

        self.ui.lb_state.setText(f"Saved [{filename}]")
        self._file_saved()

    def on_pbn_save_as_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save as")
        if len(filename) == 0:
            return

        with open(filename, "w", encoding="utf8") as fd:
            json.dump(self._dictionary, fd, indent=4)
        self._current_file = filename

        self.ui.lb_state.setText(f"Saved as [{filename}]")
        self._file_saved()

    def on_pbn_exit_clicked(self):
        if self._accept_unsaved_warning():
            return
        self.close()

    def on_pbn_search_clicked(self):
        num_lines = self._read_dict()
        self.ui.lb_state.setText(f"Searched translations of [{self._locale}]\nInserted {num_lines} lines.")

    def on_pbn_debug_clicked(self):
        data = json.dumps(self._dictionary, indent=4, ensure_ascii=False)
        data = f"{data}\n\n{json.dumps(self._row_keys_map, indent=4, ensure_ascii=False)}"
        data = f"{data}\n\nCurrent file: [{self._current_file}]"
        data = f"{data}\n\nLocale: [{self._locale}]"
        data = f"{data}\n\nVersion: v{version[0]}.{version[1]}, {version[-1]}"

        debug_win = DebugWin(self)
        debug_win.set_output(data)
        debug_win.exec()

    def on_pbn_add_clicked(self):
        if len(self._current_file) == 0:
            self.ui.lb_state.setText("There is no file opened.")
            return

        add_row_win = AddRowsWin(self)
        code = add_row_win.exec()
        if code == 0:
            return

        keys = add_row_win.txe_keys.toPlainText().split("\n")
        keys = [k for k in keys if len(k.strip()) != 0]
        succeed = 0
        fail = 0
        for k in keys:
            if k in self._dictionary:
                fail += 1
            else:
                self._dictionary[k] = {}
                succeed += 1

        self._read_dict()
        self.ui.lb_state.setText(f"Added {succeed} new keys, omitted {fail} existed keys.")
        self._file_changed()

    def on_pbn_delete_clicked(self):
        removed_keys = 0
        removed_loc = 0
        items = self.ui.tbw_words.selectedItems()
        if len(items) == 0:
            self.ui.lb_state.setText("No items selected.")
            return

        for item in items:
            key = self._row_keys_map[item.row()]
            if item.column() == 0:
                if key in self._dictionary:
                    self._dictionary.pop(key)
                    removed_keys += 1
            else:
                if key in self._dictionary and self._locale in self._dictionary[key]:
                    self._dictionary[key].pop(self._locale)
                    removed_loc += 1

        self._read_dict()
        self.ui.lb_state.setText(f"Removed {removed_keys} keys and {removed_loc} locale entries.")
        if not (removed_keys == 0 and removed_loc == 0):
            self._file_changed()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
