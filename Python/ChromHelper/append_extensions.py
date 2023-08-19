# code: utf8
import logging
import shutil
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore, QtSql

from jnlib.pyside6_utils import VerticalLine, get_sql_database
from jnlib.chromium_utils import (
    get_data_path,
    get_preferences_db,
    get_secure_preferences_db,
    get_extension_settings,
    get_protection_macs_es,
    overwrite_preferences_db,
    overwrite_secure_preferences_db,
)

from scan_extensions import scan_extensions


class UiAppendExtensionsWin(object):

    def __init__(self, window: QtWidgets.QWidget = None):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.pbn_set_temp = QtWidgets.QPushButton("设定模板", window)
        self.pbn_clear_temp = QtWidgets.QPushButton("清空模板", window)
        self.pbn_set_tar_profiles = QtWidgets.QPushButton("设定用户", window)
        self.pbn_clear_tar_profiles = QtWidgets.QPushButton("清空用户", window)
        self.pbn_append = QtWidgets.QPushButton("追加", window)
        self.pbn_update = QtWidgets.QPushButton("更新", window)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_set_temp)
        self.hly_top.addWidget(self.pbn_clear_temp)
        self.hly_top.addWidget(VerticalLine(window))
        self.hly_top.addWidget(self.pbn_set_tar_profiles)
        self.hly_top.addWidget(self.pbn_clear_tar_profiles)
        self.hly_top.addWidget(VerticalLine(window))
        self.hly_top.addWidget(self.pbn_append)
        self.hly_top.addWidget(self.pbn_update)

        self.hly_cnt = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_cnt)

        self.lw_profiles = QtWidgets.QListWidget(window)
        self.lw_profiles.setEditTriggers(QtWidgets.QListWidget.EditTrigger.NoEditTriggers)
        self.lw_profiles.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.lw_extensions = QtWidgets.QListWidget(window)
        self.lw_extensions.setEditTriggers(QtWidgets.QListWidget.EditTrigger.NoEditTriggers)
        self.lw_extensions.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.hly_cnt.addWidget(self.lw_profiles)
        self.hly_cnt.addWidget(self.lw_extensions)

        self.vly_right = QtWidgets.QVBoxLayout()
        self.hly_cnt.addLayout(self.vly_right)

        self.lne_temp_profile = QtWidgets.QLineEdit(window)
        self.lne_temp_profile.setReadOnly(True)
        self.lw_temp = QtWidgets.QListWidget(window)
        self.lw_temp.setEditTriggers(QtWidgets.QListWidget.EditTrigger.NoEditTriggers)
        self.lw_tar_profiles = QtWidgets.QListWidget(window)
        self.lw_tar_profiles.setEditTriggers(QtWidgets.QListWidget.EditTrigger.NoEditTriggers)
        self.vly_right.addWidget(self.lne_temp_profile)
        self.vly_right.addWidget(self.lw_temp)
        self.vly_right.addWidget(self.lw_tar_profiles)


class CopyThread(QtCore.QThread):

    def __init__(self, src_path: Path, dst_path: Path, parent: QtCore.QObject = None):
        super().__init__(parent)
        self.src_path = src_path
        self.dst_path = dst_path
        self.finished.connect(self.deleteLater)

    def run(self):
        if self.src_path.is_dir():
            self.dst_path.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copytree(self.src_path, self.dst_path, dirs_exist_ok=True)
            except shutil.Error:
                # LOCK 文件没有权限复制，不用管
                pass
        else:
            shutil.copyfile(self.src_path, self.dst_path)


class AppendExtensionsWin(QtWidgets.QWidget):

    def __init__(self, browser: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.browser = browser
        self.ui = UiAppendExtensionsWin(self)
        self.profile_ext_map = {}  # type: dict[str, list[dict[str, str]]]
        self.current_temp = []  # type: list[dict]
        self.tar_profiles = []  # type: list[str]

        self.load_profiles()

        self.ui.lw_profiles.itemSelectionChanged.connect(self.on_lw_profiles_item_selection_changed)
        self.ui.pbn_set_temp.clicked.connect(self.on_pbn_set_temp_clicked)
        self.ui.pbn_clear_temp.clicked.connect(self.on_pbn_clear_temp_clicked)
        self.ui.pbn_set_tar_profiles.clicked.connect(self.on_pbn_set_tar_profiles_clicked)
        self.ui.pbn_clear_tar_profiles.clicked.connect(self.on_pbn_clear_tar_profiles_clicked)
        self.ui.pbn_append.clicked.connect(self.on_pbn_append_clicked)
        self.ui.pbn_update.clicked.connect(self.on_pbn_update_clicked)

    def on_browser_changed(self, browser: str):
        self.browser = browser
        self.on_pbn_clear_temp_clicked()
        self.on_pbn_clear_tar_profiles_clicked()

        self.load_profiles()
        self.ui.lw_extensions.clear()

    def load_profiles(self):
        self.ui.lw_profiles.clear()
        self.profile_ext_map.clear()

        ext_db = scan_extensions(self.browser)
        for e in ext_db:
            info = ext_db[e]
            profiles = info["profiles"]
            for p in profiles:
                p = p.replace("%", " - ")
                self.profile_ext_map.setdefault(p, [])
                self.profile_ext_map[p].append({
                    "ids": e,
                    "name": info["name"],
                    "icon": info["icon"],
                })

        profile_names = list(self.profile_ext_map.keys())
        profile_names.sort(key=lambda x: 0 if x.split(" - ")[0] == "Default" else int(x.split(" - ")[0].split(" ", 1)[1]))
        self.ui.lw_profiles.addItems(profile_names)

    def on_pbn_set_temp_clicked(self):
        self.on_pbn_clear_temp_clicked()

        profile_name = self.ui.lw_profiles.currentItem().text()
        ext_names = [i.text() for i in self.ui.lw_extensions.selectedItems()]
        exts = self.profile_ext_map.get(profile_name, [])
        for e in exts:
            if e["name"] in ext_names:
                self.current_temp.append(e)
                self.ui.lw_temp.addItem(QtWidgets.QListWidgetItem(QtGui.QIcon(e["icon"]), e["name"]))
        self.ui.lne_temp_profile.setText(profile_name)

    def on_pbn_clear_temp_clicked(self):
        self.ui.lw_temp.clear()
        self.current_temp.clear()
        self.ui.lne_temp_profile.clear()

    def on_pbn_set_tar_profiles_clicked(self):
        self.on_pbn_clear_tar_profiles_clicked()

        profile_names = [i.text() for i in self.ui.lw_profiles.selectedItems()]
        self.tar_profiles.extend(profile_names)
        self.ui.lw_tar_profiles.addItems(profile_names)

    def on_pbn_clear_tar_profiles_clicked(self):
        self.ui.lw_tar_profiles.clear()
        self.tar_profiles.clear()

    def on_lw_profiles_item_selection_changed(self):
        self.ui.lw_extensions.clear()
        profile_name = self.ui.lw_profiles.currentItem().text()
        exts = self.profile_ext_map.get(profile_name, [])
        for e in exts:
            self.ui.lw_extensions.addItem(QtWidgets.QListWidgetItem(QtGui.QIcon(e["icon"]), e["name"]))

    def on_pbn_update_clicked(self):
        idx = self.ui.lw_profiles.currentRow()
        self.ui.lw_extensions.clear()
        self.load_profiles()
        self.ui.lw_profiles.setCurrentRow(idx)

        QtWidgets.QMessageBox.information(self, "提示", "用户和插件状态已更新。")

    def on_pbn_append_clicked(self):
        profile_name = self.ui.lne_temp_profile.text()
        if len(profile_name) == 0:
            QtWidgets.QMessageBox.critical(self, "错误", "没有设定模板用户")
            return
        data_path = get_data_path(self.browser)
        if data_path is None:
            QtWidgets.QMessageBox.critical(self, "错误", "未找到用户数据文件夹")
            return

        profile_id = profile_name.split(" - ")[0]
        s_pref_db = get_secure_preferences_db(self.browser, profile_id)
        ext_settings = get_extension_settings(self.browser, profile_id, s_pref_db)
        internal_exts = []  # type: list[tuple[Path, str, dict, str]]  # Path, ids, info, mac
        external_exts = []  # type: list[tuple[str, dict, str]]  # ids, info, mac

        for e in self.current_temp:
            ids = e["ids"]
            if ids not in ext_settings:
                continue
            ext_info = ext_settings[ids]  # type: dict
            path = ext_info["path"]  # type: str
            if path.startswith(ids):
                path_p = Path(data_path, profile_id, "Extensions", path)
                is_internal = True
            else:
                path_p = Path(path)
                is_internal = False
            if not path_p.exists():
                continue

            macs_es = get_protection_macs_es(self.browser, profile_id, s_pref_db)
            mac = macs_es.get(ids, "")

            if is_internal:
                internal_exts.append((path_p, ids, ext_info, mac))
            else:
                external_exts.append((ids, ext_info, mac))

        for p in self.tar_profiles:
            prf = p.split(" - ")[0]
            s_pref_db_i = get_secure_preferences_db(self.browser, prf)
            pref_db_i = get_preferences_db(self.browser, prf)
            ext_settings_i = get_extension_settings(self.browser, prf, s_pref_db_i, pref_db_i)
            macs_es_i = get_protection_macs_es(self.browser, prf, s_pref_db_i)

            # 已存在的插件会覆盖
            for path_p, ids, ext_info, mac in internal_exts:
                ext_settings_i[ids] = ext_info
                macs_es_i[ids] = mac
                ext_path = Path(data_path, prf, "Extensions", ids, path_p.name)

                thd_i = CopyThread(path_p, ext_path, self)
                thd_i.start()

                # CC特殊处理
                if ids == "ghgabhipcejejjmhhchfonmamedcbeod":
                    src_path = Path(data_path, profile_id, "Local Extension Settings", ids)
                    dst_path = Path(data_path, prf, "Local Extension Settings", ids)
                    if src_path.exists():
                        thd_c = CopyThread(src_path, dst_path, self)
                        thd_c.start()
                elif self.browser == "Edge" and ids == "dacknjoogbepndbemlmljdobinliojbk":
                    # Edge 的 CC 的配置数据在 Extension Cookies 文件中
                    src_ec_path = Path(data_path, profile_id, "Extension Cookies")
                    if src_ec_path.exists():
                        dst_ec_path = Path(data_path, prf, "Extension Cookies")
                        if not dst_ec_path.exists():
                            thd_c = CopyThread(src_ec_path, dst_ec_path, self)
                            thd_c.start()
                        else:
                            src_ec_db = get_sql_database(f"{self.browser}_{profile_id}_ec", str(src_ec_path))
                            if not src_ec_db.open():
                                logging.error(f"在 Edge 中拷贝 CC 插件时未能打开 {profile_id} 的 Extension Cookies 文件")
                            else:
                                dst_ec_db = get_sql_database(f"{self.browser}_{prf}_ec", str(dst_ec_path))
                                if not dst_ec_db.open():
                                    logging.error(f"在 Edge 中拷贝 CC 插件时未能打开 {prf} 的 Extension Cookies 文件")
                                else:
                                    ec_query = QtSql.QSqlQuery(dst_ec_db)
                                    ec_query.exec(f"ATTACH DATABASE '{str(src_ec_path)}' AS src_ec_db;")
                                    ec_query.exec(f"INSERT INTO cookies SELECT * FROM src_ec_db.cookies WHERE host_key='{ids}';")
                                    logging.info(f"以从 {profile_id} 向 {prf} 的 Extension Cookies 插入 CC 配置")

            for ids, ext_info, mac in external_exts:
                ext_settings_i[ids] = ext_info
                macs_es_i[ids] = mac
                # 离线插件不需要复制目录

            overwrite_preferences_db(pref_db_i, self.browser, prf)
            overwrite_secure_preferences_db(s_pref_db_i, self.browser, prf)

        total = len(self.tar_profiles)
        self.on_pbn_clear_tar_profiles_clicked()

        QtWidgets.QMessageBox.information(
            self, "信息",
            f"已为 {total} 个用户追加 {len(internal_exts)} 个在线插件和 {len(external_exts)} 个离线插件。"
        )
