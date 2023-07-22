# code: utf8

#
# Change log
#
# v0.1
# 1. 仅支持 谷歌，不能检测浏览器的开启与否
#

#########################
#  ____   _____  _____  #
# |  _ \ / ____|/ ____| #
# | |_) | (___ | |      #
# |  _ < \___ \| |      #
# | |_) |____) | |____  #
# |____/|_____/ \_____| #
#########################

import os
import sys
import json
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui, QtSql

version = (0, 1, 20230722)

_BROWSERS = ["Chrome", "Edge", "Brave"]

_PLAT = sys.platform
_USER_PATH = os.path.expanduser("~")
_DATA_PATH_MAP = {
    "win32": {
        "Chrome": Path(_USER_PATH, "AppData", "Local", "Google", "Chrome", "User Data"),
        "Edge": Path(_USER_PATH, "AppData", "Local", "Microsoft", "Edge", "User Data"),
        "Brave": Path(_USER_PATH, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data"),
    },
    "darwin": {
        "Chrome": Path(_USER_PATH, "Library", "Application Support", "Google", "Chrome"),
        "Edge": Path(_USER_PATH, "Library", "Application Support", "Microsoft Edge"),
        "Brave": Path(_USER_PATH, "Library", "Application Support", "BraveSoftware", "Brave-Browser"),
    },
}


def get_local_state_db(browser: str) -> dict:
    data_path = _DATA_PATH_MAP[_PLAT].get(browser, None)  # type: Path | None
    if data_path is None or not data_path.exists():
        return {}

    local_state_path = Path(data_path, "Local State")
    if not local_state_path.exists():
        return {}

    with open(local_state_path, "r", encoding="utf8") as f:
        lst_db = json.load(f)

    return lst_db


def get_preferences_path(browser: str, profile: str) -> Path | None:
    data_path = _DATA_PATH_MAP[_PLAT].get(browser, None)  # type: Path | None
    if data_path is None or not data_path.exists():
        return None

    preferences_path = Path(data_path, profile, "Preferences")
    if not preferences_path.exists():
        return None

    return preferences_path


def get_preferences_db(browser: str, profile: str) -> dict:
    preferences_path = get_preferences_path(browser, profile)
    if preferences_path is None:
        return {}

    with open(preferences_path, "r", encoding="utf8") as f:
        pref_db = json.load(f)

    return pref_db


def overwrite_preferences_db(new_pref_db: dict, browser: str, profile: str) -> bool:
    preferences_path = get_preferences_path(browser, profile)
    if preferences_path is None:
        return False

    with open(preferences_path, "w", encoding="utf8") as f:
        json.dump(new_pref_db, f)

    return True


def get_x_in_profile_path(browser: str, profile: str, x: str) -> Path | None:
    data_path = _DATA_PATH_MAP[_PLAT].get(browser, None)  # type: Path | None
    if data_path is None or not data_path.exists():
        return None

    x_path = Path(data_path, profile, x)
    if not x_path.exists():
        return None

    return x_path


def get_with_chained_keys(dic: dict, keys: list[str, ...]):
    k = keys[0]
    if k not in dic:
        return None
    if len(keys) == 1:
        return dic[k]
    return get_with_chained_keys(dic[k], keys[1:])


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(750, 600)
        window.setWindowTitle(f"浏览器设置检查 v{version[0]}.{version[1]}.{version[-1]}")

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_browser = QtWidgets.QLabel("切换浏览器：", window)
        self.cmbx_browser = QtWidgets.QComboBox(window)
        self.cmbx_browser.addItems(_BROWSERS)
        self.pbn_refresh = QtWidgets.QPushButton("刷新", window)
        self.pbn_apply = QtWidgets.QPushButton("应用", window)
        self.pbn_apply_all = QtWidgets.QPushButton("应用所有", window)

        self.hly_top.addWidget(self.lb_browser)
        self.hly_top.addWidget(self.cmbx_browser)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_refresh)
        self.hly_top.addWidget(self.pbn_apply)
        self.hly_top.addWidget(self.pbn_apply_all)

        self.hln_top = QtWidgets.QFrame(window)
        self.hln_top.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.hln_top.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.vly_m.addWidget(self.hln_top)

        self.hly_mid = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_mid)

        self.lw_profiles = QtWidgets.QListWidget(window)
        self.lw_profiles.setSelectionMode(QtWidgets.QListWidget.SelectionMode.SingleSelection)
        self.hly_mid.addWidget(self.lw_profiles)

        self.sa_settings = QtWidgets.QScrollArea(window)
        self.sa_settings.setWidgetResizable(True)
        self.hly_mid.addWidget(self.sa_settings)

        self.hly_mid.setStretch(0, 1)
        self.hly_mid.setStretch(1, 5)

        self.tw_sa_settings = QtWidgets.QTabWidget(self.sa_settings)
        self.sa_settings.setWidget(self.tw_sa_settings)

        # ============ 谷歌 ========================

        self.wg_tab_google = QtWidgets.QWidget()
        self.tw_sa_settings.addTab(self.wg_tab_google, "谷歌（通用）")

        self.vly_wg_tab_google = QtWidgets.QVBoxLayout()
        self.wg_tab_google.setLayout(self.vly_wg_tab_google)

        self.gbx_password = QtWidgets.QGroupBox("密码管理工具", self.wg_tab_google)
        self.vly_wg_tab_google.addWidget(self.gbx_password)

        self.hly_gbx_password = QtWidgets.QHBoxLayout()
        self.gbx_password.setLayout(self.hly_gbx_password)

        self.cbx_save_pass = QtWidgets.QCheckBox("提示保存密码", self.gbx_password)
        self.cbx_auto_signin = QtWidgets.QCheckBox("自动登录", self.gbx_password)
        self.hly_gbx_password.addWidget(self.cbx_save_pass)
        self.hly_gbx_password.addWidget(self.cbx_auto_signin)
        self.hly_gbx_password.addStretch(1)

        self.gbx_payment = QtWidgets.QGroupBox("付款方式", self.wg_tab_google)
        self.vly_wg_tab_google.addWidget(self.gbx_payment)

        self.hly_gbx_payment = QtWidgets.QHBoxLayout()
        self.gbx_payment.setLayout(self.hly_gbx_payment)

        self.cbx_save_card = QtWidgets.QCheckBox("保存并填写付款方式", self.gbx_payment)
        self.cbx_make_payment = QtWidgets.QCheckBox("允许网站检查您是否已保存付款方式", self.gbx_payment)
        self.hly_gbx_payment.addWidget(self.cbx_save_card)
        self.hly_gbx_payment.addWidget(self.cbx_make_payment)
        self.hly_gbx_payment.addStretch(1)

        self.gbx_address = QtWidgets.QGroupBox("地址和其他信息", self.wg_tab_google)
        self.vly_wg_tab_google.addWidget(self.gbx_address)

        self.hly_gbx_address = QtWidgets.QHBoxLayout()
        self.gbx_address.setLayout(self.hly_gbx_address)

        self.cbx_save_addr = QtWidgets.QCheckBox("保存并填写地址", self.gbx_address)
        self.hly_gbx_address.addWidget(self.cbx_save_addr)
        self.hly_gbx_address.addStretch(1)

        self.gbx_cookies = QtWidgets.QGroupBox("Cookie 及其他网站数据", self.wg_tab_google)
        self.vly_wg_tab_google.addWidget(self.gbx_cookies)

        self.hly_gbx_cookies = QtWidgets.QHBoxLayout()
        self.gbx_cookies.setLayout(self.hly_gbx_cookies)

        self.cbx_clear_cookies = QtWidgets.QCheckBox("关闭所有窗口时清除 Cookie 及网站数据", self.gbx_cookies)
        self.cbx_not_track = QtWidgets.QCheckBox("将“Do Not Track”请求与浏览流量一起发送", self.gbx_cookies)
        self.hly_gbx_cookies.addWidget(self.cbx_clear_cookies)
        self.hly_gbx_cookies.addWidget(self.cbx_not_track)
        self.hly_gbx_cookies.addStretch(1)

        self.gbx_site = QtWidgets.QGroupBox("网站设置", self.wg_tab_google)
        self.vly_wg_tab_google.addWidget(self.gbx_site)

        self.hly_gbx_site = QtWidgets.QHBoxLayout()
        self.gbx_site.setLayout(self.hly_gbx_site)

        self.cbx_forbid_location = QtWidgets.QCheckBox("不允许网站查看您所在的位置", self.gbx_site)
        self.hly_gbx_site.addWidget(self.cbx_forbid_location)
        self.hly_gbx_site.addStretch(1)

        self.gbx_others = QtWidgets.QGroupBox("其他", self.wg_tab_google)
        self.vly_wg_tab_google.addWidget(self.gbx_others)

        self.gly_gbx_others = QtWidgets.QGridLayout()
        self.gbx_others.setLayout(self.gly_gbx_others)

        self.tbv_browser_engines = QtWidgets.QTableView(self.gbx_others)
        self.tbv_browser_engines.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbv_browser_engines.horizontalHeader().setStretchLastSection(True)
        self.gly_gbx_others.addWidget(self.tbv_browser_engines, 1, 0)

        self.cbx_clear_browser_engines = QtWidgets.QCheckBox("移除列举的搜索引擎", self.gbx_others)
        self.gly_gbx_others.addWidget(self.cbx_clear_browser_engines, 0, 0)

        self.tbv_saved_pass = QtWidgets.QTableView(self.gbx_others)
        self.tbv_saved_pass.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbv_saved_pass.horizontalHeader().setStretchLastSection(True)
        self.gly_gbx_others.addWidget(self.tbv_saved_pass, 1, 1)

        self.cbx_clear_saved_pass = QtWidgets.QCheckBox("移除保存的密码", self.gbx_others)
        self.gly_gbx_others.addWidget(self.cbx_clear_saved_pass, 0, 1)

        # 移除保存的密码暂不支持
        self.cbx_clear_saved_pass.setText(f"{self.cbx_clear_saved_pass.text()}（暂不支持）")
        self.cbx_clear_saved_pass.setEnabled(False)

        # ============ 微软 ========================

        self.wg_tab_edge = QtWidgets.QWidget()
        self.tw_sa_settings.addTab(self.wg_tab_edge, "微软（特有）")

        self.vly_wg_tab_edge = QtWidgets.QVBoxLayout()
        self.wg_tab_edge.setLayout(self.vly_wg_tab_edge)


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)

        self._SELECT_ENGINES_Q = """
            SELECT short_name, keyword FROM keywords
            WHERE favicon_url<>"" AND keyword<>"google.com";
        """
        self._DELETE_ENGINES_Q = """
            DELETE FROM keywords
            WHERE favicon_url<>"" AND keyword<>"google.com";
        """
        self._SELECT_PASSWORDS_Q = """
            SELECT group_display_name FROM eq_classes;
        """
        self._DELETE_PASSWORDS_Q_L = ["""
            DELETE FROM eq_class_groups
            WHERE set_id IN (SELECT id FROM eq_classes);
        """, """
            DELETE FROM eq_class_members
            WHERE set_id IN (SELECT id FROM eq_classes);
        """, """
            DELETE FROM eq_classes;
        """]

        self.refresh_profiles(self.ui.cmbx_browser.currentText())

        self.ui.cmbx_browser.currentTextChanged.connect(self.on_cmbx_browsers_current_text_changed)
        self.ui.lw_profiles.itemSelectionChanged.connect(self.on_lw_profiles_item_selection_changed)
        self.ui.pbn_refresh.clicked.connect(self.on_pbn_refresh_clicked)
        self.ui.pbn_apply.clicked.connect(self.on_pbn_apply_clicked)
        self.ui.pbn_apply_all.clicked.connect(self.on_pbn_apply_all_clicked)

    def _get_current_item(self) -> QtWidgets.QListWidgetItem | None:
        item = self.ui.lw_profiles.currentItem()
        if item is None:
            QtWidgets.QMessageBox.information(self, "提示", "当前没有选中的浏览器用户。")
            return None

        return item

    def on_pbn_refresh_clicked(self):
        item = self._get_current_item()
        if item is None:
            return

        self.update_profile_settings(self.ui.cmbx_browser.currentText(), item.text())

    def on_lw_profiles_item_selection_changed(self):
        self.update_profile_settings(
            self.ui.cmbx_browser.currentText(),
            self.ui.lw_profiles.currentItem().text())

    def on_cmbx_browsers_current_text_changed(self, text: str):
        self.refresh_profiles(text)

    @staticmethod
    def _get_browser_profiles(browser: str) -> list | None:
        lst_db = get_local_state_db(browser)
        profiles_dic = get_with_chained_keys(lst_db, ["profile", "info_cache"])
        if profiles_dic is None:
            return None

        profiles = list(profiles_dic.keys())
        profiles.sort(key=lambda x: 0 if x == "Default" else int(x.split(" ")[1]))

        return profiles

    def refresh_profiles(self, browser: str):
        profiles = self._get_browser_profiles(browser)
        if profiles is None:
            QtWidgets.QMessageBox.critical(
                self, "错误",
                f"在 {browser} 的 Local State 文件中找不到 profile>info_cache。")
            return

        self.ui.lw_profiles.clear()
        self.ui.lw_profiles.addItems(profiles)

    @staticmethod
    def _update_check_box(check_box: QtWidgets.QCheckBox, value: bool | None, default: bool):
        if value is None:
            check_box.setChecked(default)
        else:
            check_box.setChecked(value)

    def update_profile_settings(self, browser: str, profile: str):
        pref_db = get_preferences_db(browser, profile)
        self._update_check_box(self.ui.cbx_save_pass,
                               get_with_chained_keys(pref_db, ["credentials_enable_service"]), True)
        self._update_check_box(self.ui.cbx_auto_signin,
                               get_with_chained_keys(pref_db, ["credentials_enable_autosignin"]), True)
        self._update_check_box(self.ui.cbx_save_card,
                               get_with_chained_keys(pref_db, ["autofill", "credit_card_enabled"]), True)
        self._update_check_box(self.ui.cbx_make_payment,
                               get_with_chained_keys(pref_db, ["payments", "can_make_payment_enabled"]), True)
        self._update_check_box(self.ui.cbx_save_addr,
                               get_with_chained_keys(pref_db, ["autofill", "profile_enabled"]), True)
        self._update_check_box(self.ui.cbx_not_track,
                               get_with_chained_keys(pref_db, ["enable_do_not_track"]), False)

        dcsv = get_with_chained_keys(pref_db, ["profile", "default_content_setting_values"])
        if dcsv is None:
            self._update_check_box(self.ui.cbx_clear_cookies, None, False)
            self._update_check_box(self.ui.cbx_forbid_location, None, False)
        else:
            self._update_check_box(self.ui.cbx_clear_cookies, "cookies" in dcsv and dcsv["cookies"] == 4, False)
            self._update_check_box(self.ui.cbx_forbid_location,
                                   "geolocation" in dcsv and dcsv["geolocation"] == 2, False)

        wd_sqm = self._get_web_data_db_model(browser, profile)
        if wd_sqm is not None:
            self.ui.tbv_browser_engines.setModel(wd_sqm)

        af_sqm = self._get_affiliation_db_model(browser, profile)
        if af_sqm is not None:
            self.ui.tbv_saved_pass.setModel(af_sqm)

    @staticmethod
    def _get_database(conn_name: str, file_path: str) -> QtSql.QSqlDatabase:
        if QtSql.QSqlDatabase.contains(conn_name):
            db = QtSql.QSqlDatabase.database(conn_name, open=False)
        else:
            db = QtSql.QSqlDatabase.addDatabase("QSQLITE", conn_name)
            db.setDatabaseName(file_path)

        return db

    def _get_web_data_db_model(self, browser: str, profile: str) -> QtSql.QSqlQueryModel | None:
        web_data_path = get_x_in_profile_path(browser, profile, "Web Data")
        if web_data_path is None:
            return None

        webdata_db = self._get_database(f"{browser}_{profile}_webdata", str(web_data_path))
        if not webdata_db.open():
            return None

        sqm = QtSql.QSqlQueryModel(self)
        sqm.setQuery(self._SELECT_ENGINES_Q, webdata_db)
        sqm.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "搜索引擎")
        sqm.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "网址")
        return sqm

    def _get_affiliation_db_model(self, browser: str, profile: str) -> QtSql.QSqlQueryModel | None:
        affiliation_path = get_x_in_profile_path(browser, profile, "Affiliation Database")
        if affiliation_path is None:
            return None

        affiliation_db = self._get_database(f"{browser}_{profile}_affiliation", str(affiliation_path))
        if not affiliation_db.open():
            return None

        sqm = QtSql.QSqlQueryModel(self)
        sqm.setQuery(self._SELECT_PASSWORDS_Q, affiliation_db)
        sqm.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "网址")
        return sqm

    def on_pbn_apply_clicked(self):
        item = self._get_current_item()
        if item is None:
            return

        browser = self.ui.cmbx_browser.currentText()
        profile = item.text()
        self.apply_one_profile_settings(
            browser, profile,
            save_pass=self.ui.cbx_save_pass.checkState() == QtCore.Qt.CheckState.Checked,
            auto_signin=self.ui.cbx_auto_signin.checkState() == QtCore.Qt.CheckState.Checked,
            save_card=self.ui.cbx_save_card.checkState() == QtCore.Qt.CheckState.Checked,
            save_addr=self.ui.cbx_save_addr.checkState() == QtCore.Qt.CheckState.Checked,
            make_payment=self.ui.cbx_make_payment.checkState() == QtCore.Qt.CheckState.Checked,
            not_track=self.ui.cbx_not_track.checkState() == QtCore.Qt.CheckState.Checked,
            clear_cookies=self.ui.cbx_clear_cookies.checkState() == QtCore.Qt.CheckState.Checked,
            forbid_location=self.ui.cbx_forbid_location.checkState() == QtCore.Qt.CheckState.Checked,
            clear_browser_engines=self.ui.cbx_clear_browser_engines.checkState() == QtCore.Qt.CheckState.Checked,
            clear_saved_pass=self.ui.cbx_clear_saved_pass.checkState() == QtCore.Qt.CheckState.Checked,
            is_current=True
        )

        self.update_profile_settings(browser, profile)

        QtWidgets.QMessageBox.information(
            self, "提示",
            f"{browser} > {profile} 已应用当前设置。"
        )

    def on_pbn_apply_all_clicked(self):
        item = self._get_current_item()
        if item is None:
            cur_profile = ""
        else:
            cur_profile = item.text()

        browser = self.ui.cmbx_browser.currentText()
        profiles = self._get_browser_profiles(browser)

        save_pass = self.ui.cbx_save_pass.checkState() == QtCore.Qt.CheckState.Checked
        auto_signin = self.ui.cbx_auto_signin.checkState() == QtCore.Qt.CheckState.Checked
        save_card = self.ui.cbx_save_card.checkState() == QtCore.Qt.CheckState.Checked
        save_addr = self.ui.cbx_save_addr.checkState() == QtCore.Qt.CheckState.Checked
        make_payment = self.ui.cbx_make_payment.checkState() == QtCore.Qt.CheckState.Checked
        not_track = self.ui.cbx_not_track.checkState() == QtCore.Qt.CheckState.Checked
        clear_cookies = self.ui.cbx_clear_cookies.checkState() == QtCore.Qt.CheckState.Checked
        forbid_location = self.ui.cbx_forbid_location.checkState() == QtCore.Qt.CheckState.Checked
        clear_browser_engines = self.ui.cbx_clear_browser_engines.checkState() == QtCore.Qt.CheckState.Checked
        clear_saved_pass = self.ui.cbx_clear_saved_pass.checkState() == QtCore.Qt.CheckState.Checked

        for profile in profiles:
            is_current = profile == cur_profile

            self.apply_one_profile_settings(
                browser, profile,
                save_pass=save_pass,
                auto_signin=auto_signin,
                save_card=save_card,
                save_addr=save_addr,
                make_payment=make_payment,
                not_track=not_track,
                clear_cookies=clear_cookies,
                forbid_location=forbid_location,
                clear_browser_engines=clear_browser_engines,
                clear_saved_pass=clear_saved_pass,
                is_current=is_current
            )

            if is_current:
                self.update_profile_settings(browser, profile)

        QtWidgets.QMessageBox.information(
            self, "提示",
            f"{browser} 的所有用户 已应用当前设置。"
        )

    def apply_one_profile_settings(
            self, browser: str, profile: str, *,
            save_pass: bool, auto_signin: bool, save_card: bool, save_addr: bool,
            make_payment: bool, not_track: bool, clear_cookies: bool, forbid_location: bool,
            clear_browser_engines: bool, clear_saved_pass: bool, is_current: bool,
    ):
        pref_db = get_preferences_db(browser, profile)

        new_settings = {
            "credentials_enable_service": save_pass,
            "credentials_enable_autosignin": auto_signin,
            "autofill": {
                "credit_card_enabled": save_card,
                "profile_enabled": save_addr,
            },
            "payments": {
                "can_make_payment_enabled": make_payment,
            },
            "enable_do_not_track": not_track,
            "profile": {
                "default_content_setting_values": {},
            }
        }
        pref_db.update(new_settings)

        dcsv = pref_db["profile"]["default_content_setting_values"]  # type: dict
        if clear_cookies:
            dcsv["cookies"] = 4
        else:
            if "cookies" in dcsv:
                dcsv.pop("cookies")

        if forbid_location:
            dcsv["geolocation"] = 2
        else:
            if "geolocation" in dcsv:
                dcsv.pop("geolocation")

        overwrite_preferences_db(pref_db, browser, profile)

        if clear_browser_engines:
            web_data_path = get_x_in_profile_path(browser, profile, "Web Data")
            if web_data_path is not None:
                webdata_db = self._get_database(f"{browser}_{profile}_webdata", str(web_data_path))
                if webdata_db.isOpen() or webdata_db.open():
                    wd_query = QtSql.QSqlQuery(webdata_db)
                    wd_query.exec(self._DELETE_ENGINES_Q)

                    if is_current:
                        wd_sqm = self.ui.tbv_browser_engines.model()  # type: QtSql.QSqlQueryModel
                        wd_sqm.setQuery(self._SELECT_ENGINES_Q, webdata_db)

        if clear_saved_pass:
            affiliation_path = get_x_in_profile_path(browser, profile, "Affiliation Database")
            if affiliation_path is not None:
                affiliation_db = self._get_database(f"{browser}_{profile}_affiliation", str(affiliation_path))
                if affiliation_db.isOpen() or affiliation_db.open():
                    af_query = QtSql.QSqlQuery(affiliation_db)
                    for q in self._DELETE_PASSWORDS_Q_L:
                        af_query.exec(q)

                    if is_current:
                        af_sqm = self.ui.tbv_saved_pass.model()  # type: QtSql.QSqlQueryModel
                        af_sqm.setQuery(self._SELECT_PASSWORDS_Q, affiliation_db)

    # def resizeEvent(self, event: QtGui.QResizeEvent):
    #     print(event.size())


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
