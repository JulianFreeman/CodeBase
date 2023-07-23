# code: utf8

#
# Change log
#
# v1.1
# 1. 增加显示当前用户名
#
# v1.0
# 1. 支持 Edge，Brave；浏览器用户运行状态下应用无效
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

import bsc_rc

version = (1, 1, 20230723)

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


def get_with_chained_keys(dic: dict, keys: list[str, ...]):
    k = keys[0]
    if k not in dic:
        return None
    if len(keys) == 1:
        return dic[k]
    return get_with_chained_keys(dic[k], keys[1:])


def append_dictionary(dic: dict, sub_dic: dict):
    for k in sub_dic:
        if not ((k in dic and isinstance(dic[k], dict)) and isinstance(sub_dic[k], dict)):
            dic[k] = sub_dic[k]
            continue

        append_dictionary(dic[k], sub_dic[k])


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


def change_color(widget: QtWidgets.QWidget, color: str | QtCore.Qt.GlobalColor):
    pal = widget.palette()
    pal.setColor(QtGui.QPalette.ColorRole.WindowText, color)
    widget.setPalette(pal)


class UiMainWin(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(750, 600)
        window.setWindowTitle(f"浏览器设置检查 v{version[0]}.{version[1]}.{version[-1]}")
        window.setWindowIcon(QtGui.QIcon(":/bsc_16.png"))

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lb_browser = QtWidgets.QLabel("切换浏览器：", window)
        self.cmbx_browser = QtWidgets.QComboBox(window)
        self.cmbx_browser.addItems(_BROWSERS)
        self.lb_profile = QtWidgets.QLabel("当前用户名：", window)
        self.lne_profile = QtWidgets.QLineEdit(window)
        self.lne_profile.setReadOnly(True)
        self.pbn_refresh = QtWidgets.QPushButton("刷新", window)
        self.pbn_apply = QtWidgets.QPushButton("应用", window)
        self.pbn_apply_all = QtWidgets.QPushButton("应用所有", window)

        self.hly_top.addWidget(self.lb_browser)
        self.hly_top.addWidget(self.cmbx_browser)
        self.hly_top.addWidget(self.lb_profile)
        self.hly_top.addWidget(self.lne_profile)
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
        self.tw_sa_settings.addTab(self.wg_tab_google, "Chrome（通用）")

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

        self.cbx_clear_browser_engines = QtWidgets.QCheckBox("移除列举的搜索引擎（除了谷歌）", self.gbx_others)
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
        change_color(self.cbx_clear_saved_pass, QtCore.Qt.GlobalColor.darkGray)

        # ============ 微软 ========================

        self.wg_tab_edge = QtWidgets.QWidget()
        self.tw_sa_settings.addTab(self.wg_tab_edge, "Edge（特有）")

        self.vly_wg_tab_edge = QtWidgets.QVBoxLayout()
        self.wg_tab_edge.setLayout(self.vly_wg_tab_edge)

        self.lb_edge_applicable = QtWidgets.QLabel("*不适用于当前浏览器", self.wg_tab_edge)
        self.vly_wg_tab_edge.addWidget(self.lb_edge_applicable)
        change_color(self.lb_edge_applicable, QtCore.Qt.GlobalColor.red)
        self.lb_edge_applicable.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        self.gbx_edge_personal = QtWidgets.QGroupBox("个人资料", self.wg_tab_edge)
        self.vly_wg_tab_edge.addWidget(self.gbx_edge_personal)

        self.gly_gbx_edge_personal = QtWidgets.QGridLayout()
        self.gbx_edge_personal.setLayout(self.gly_gbx_edge_personal)

        self.cbx_edge_rewards = QtWidgets.QCheckBox("在 Microsoft Edge 中赚取 Microsoft Rewards", self.gbx_edge_personal)
        self.cbx_edge_custom_data = QtWidgets.QCheckBox("保存并填写自定义信息", self.gbx_edge_personal)
        self.cbx_edge_wallet_checkout = QtWidgets.QCheckBox("购物时在网站上显示快速结帐", self.gbx_edge_personal)
        self.gly_gbx_edge_personal.addWidget(self.cbx_edge_rewards, 0, 0)
        self.gly_gbx_edge_personal.addWidget(self.cbx_edge_custom_data, 0, 1)
        self.gly_gbx_edge_personal.addWidget(self.cbx_edge_wallet_checkout, 1, 0)

        self.gbx_edge_exit_clear = QtWidgets.QGroupBox("关闭时清除浏览数据", self.wg_tab_edge)
        self.vly_wg_tab_edge.addWidget(self.gbx_edge_exit_clear)

        self.gly_gbx_edge_exit_clear = QtWidgets.QGridLayout()
        self.gbx_edge_exit_clear.setLayout(self.gly_gbx_edge_exit_clear)

        self.cbx_edge_ec_browsing_history = QtWidgets.QCheckBox("浏览历史记录", self.gbx_edge_exit_clear)
        self.cbx_edge_ec_download_history = QtWidgets.QCheckBox("下载历史记录", self.gbx_edge_exit_clear)
        self.cbx_edge_ec_cookies = QtWidgets.QCheckBox("Cookie 和其他站点数据", self.gbx_edge_exit_clear)
        self.cbx_edge_ec_cache = QtWidgets.QCheckBox("缓存的图像和文件", self.gbx_edge_exit_clear)
        self.cbx_edge_ec_passwords = QtWidgets.QCheckBox("密码", self.gbx_edge_exit_clear)
        self.cbx_edge_ec_form_data = QtWidgets.QCheckBox("自动填充表单数据(包括表单和卡)", self.gbx_edge_exit_clear)
        self.cbx_edge_ec_site_settings = QtWidgets.QCheckBox("站点权限", self.gbx_edge_exit_clear)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_browsing_history, 0, 0)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_download_history, 1, 0)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_cookies, 2, 0)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_cache, 3, 0)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_passwords, 0, 1)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_form_data, 1, 1)
        self.gly_gbx_edge_exit_clear.addWidget(self.cbx_edge_ec_site_settings, 2, 1)

        self.gbx_edge_service = QtWidgets.QGroupBox("服务", self.wg_tab_edge)
        self.vly_wg_tab_edge.addWidget(self.gbx_edge_service)

        self.gly_gbx_edge_service = QtWidgets.QGridLayout()
        self.gbx_edge_service.setLayout(self.gly_gbx_edge_service)

        self.cbx_edge_personal_data = QtWidgets.QCheckBox("个性化和广告", self.gbx_edge_service)
        self.cbx_edge_nav_err = QtWidgets.QCheckBox("使用 Web 服务帮助解决导航错误", self.gbx_edge_service)
        self.cbx_edge_alt_err = QtWidgets.QCheckBox("找不到网站时建议类似的站点", self.gbx_edge_service)
        self.cbx_edge_shopping_assist = QtWidgets.QCheckBox("在 Microsoft Edge中购物，节省时间和金钱", self.gbx_edge_service)
        self.cbx_edge_follow = QtWidgets.QCheckBox("在 Microsoft Edge 中显示关注创建者的建议", self.gbx_edge_service)
        self.cbx_edge_follow_notif = QtWidgets.QCheckBox("在你关注的创建者发布新内容时收到通知", self.gbx_edge_service)
        self.cbx_edge_tipping_assist = QtWidgets.QCheckBox("显示支持你关注的事业和非盈利组织的机会", self.gbx_edge_service)
        self.cbx_edge_under_trig = QtWidgets.QCheckBox("获取有关使用“发现”浏览相关内容的通知", self.gbx_edge_service)
        self.cbx_edge_tab_services = QtWidgets.QCheckBox("让 Microsoft Edge 帮助保持标签页井然有序", self.gbx_edge_service)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_personal_data, 0, 0)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_nav_err, 1, 0)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_alt_err, 2, 0)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_shopping_assist, 3, 0)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_follow, 4, 0)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_follow_notif, 0, 1)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_tipping_assist, 1, 1)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_under_trig, 2, 1)
        self.gly_gbx_edge_service.addWidget(self.cbx_edge_tab_services, 3, 1)

        self.lb_edge_reminder = QtWidgets.QLabel("*记得检查第一栏通用中的设置")
        change_color(self.lb_edge_reminder, QtCore.Qt.GlobalColor.blue)
        self.lb_edge_reminder.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.vly_wg_tab_edge.addWidget(self.lb_edge_reminder)

        self.vly_wg_tab_edge.addStretch(1)

        # ============ 狮子头 ========================

        self.wg_tab_brave = QtWidgets.QWidget()
        self.tw_sa_settings.addTab(self.wg_tab_brave, "Brave（特有）")

        self.vly_wg_tab_brave = QtWidgets.QVBoxLayout()
        self.wg_tab_brave.setLayout(self.vly_wg_tab_brave)

        self.lb_brave_applicable = QtWidgets.QLabel("*不适用于当前浏览器", self.wg_tab_brave)
        self.vly_wg_tab_brave.addWidget(self.lb_brave_applicable)
        change_color(self.lb_brave_applicable, QtCore.Qt.GlobalColor.red)
        self.lb_brave_applicable.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        self.gbx_brave_tools = QtWidgets.QGroupBox("一些功能", self.wg_tab_brave)
        self.vly_wg_tab_brave.addWidget(self.gbx_brave_tools)

        self.gly_gbx_brave_tools = QtWidgets.QGridLayout()
        self.gbx_brave_tools.setLayout(self.gly_gbx_brave_tools)

        self.cbx_brave_news = QtWidgets.QCheckBox("在地址栏显示 Brave 新闻按钮", self.gbx_brave_tools)
        self.cbx_brave_vpn = QtWidgets.QCheckBox("显示 VPN 按钮", self.gbx_brave_tools)
        self.cbx_brave_rewards = QtWidgets.QCheckBox("在地址栏显示 Brave 奖励图标", self.gbx_brave_tools)
        self.cbx_brave_rewards_tip = QtWidgets.QCheckBox("在网站上显示 Brave 奖励提示按钮", self.gbx_brave_tools)
        self.cbx_brave_wallet = QtWidgets.QCheckBox("在工具栏上显示 Brave Wallet 图标", self.gbx_brave_tools)
        self.cbx_brave_wayback = QtWidgets.QCheckBox("显示 404 页上的 Wayback Machine 提示", self.gbx_brave_tools)
        self.gly_gbx_brave_tools.addWidget(self.cbx_brave_news, 0, 0)
        self.gly_gbx_brave_tools.addWidget(self.cbx_brave_vpn, 1, 0)
        self.gly_gbx_brave_tools.addWidget(self.cbx_brave_rewards, 0, 1)
        self.gly_gbx_brave_tools.addWidget(self.cbx_brave_rewards_tip, 1, 1)
        self.gly_gbx_brave_tools.addWidget(self.cbx_brave_wallet, 2, 0)
        self.gly_gbx_brave_tools.addWidget(self.cbx_brave_wayback, 2, 1)

        self.gbx_brave_clear_data = QtWidgets.QGroupBox("退出时清除数据", self.wg_tab_brave)
        self.vly_wg_tab_brave.addWidget(self.gbx_brave_clear_data)

        self.gly_gbx_brave_clear_data = QtWidgets.QGridLayout()
        self.gbx_brave_clear_data.setLayout(self.gly_gbx_brave_clear_data)

        self.cbx_brave_cd_browsing_history = QtWidgets.QCheckBox("浏览记录", self.gbx_brave_clear_data)
        self.cbx_brave_cd_cache = QtWidgets.QCheckBox("缓存的图片及文件", self.gbx_brave_clear_data)
        self.cbx_brave_cd_cookies = QtWidgets.QCheckBox("Cookie 及其它网站数据", self.gbx_brave_clear_data)
        self.cbx_brave_cd_download_history = QtWidgets.QCheckBox("下载记录", self.gbx_brave_clear_data)
        self.cbx_brave_cd_form_data = QtWidgets.QCheckBox("自动填充表单数据", self.gbx_brave_clear_data)
        self.cbx_brave_cd_hosted_apps_data = QtWidgets.QCheckBox("托管应用数据", self.gbx_brave_clear_data)
        self.cbx_brave_cd_passwords = QtWidgets.QCheckBox("密码和其他登录数据", self.gbx_brave_clear_data)
        self.cbx_brave_cd_site_settings = QtWidgets.QCheckBox("站点和屏蔽设置", self.gbx_brave_clear_data)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_browsing_history, 0, 0)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_cache, 1, 0)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_cookies, 2, 0)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_download_history, 3, 0)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_form_data, 0, 1)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_hosted_apps_data, 1, 1)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_passwords, 2, 1)
        self.gly_gbx_brave_clear_data.addWidget(self.cbx_brave_cd_site_settings, 3, 1)

        self.lb_brave_reminder = QtWidgets.QLabel("*记得检查第一栏通用中的设置")
        change_color(self.lb_brave_reminder, QtCore.Qt.GlobalColor.blue)
        self.lb_brave_reminder.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.vly_wg_tab_brave.addWidget(self.lb_brave_reminder)

        self.vly_wg_tab_brave.addStretch(1)


class MainWin(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.ui = UiMainWin(self)

        self._SELECT_ENGINES_Q = """
            SELECT short_name, keyword FROM keywords
            WHERE favicon_url<>"";
        """
        self._DELETE_ENGINES_Q = """
            DELETE FROM keywords
            WHERE favicon_url<>"" AND short_name<>"Google";
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

        self.on_cmbx_browsers_current_text_changed(_BROWSERS[0])

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
        browser = self.ui.cmbx_browser.currentText()
        profile = self.ui.lw_profiles.currentItem().text()
        _, profile_dic = self._get_browser_profiles(browser)
        if profile_dic is None:
            name = "[未找到]"
        else:
            name = get_with_chained_keys(profile_dic, [profile, "shortcut_name"])
            if name is None:
                name = get_with_chained_keys(profile_dic, [profile, "name"])
            name = "[未找到]" if name is None else name

        self.ui.lne_profile.setText(name)
        self.update_profile_settings(browser, profile)

    def on_cmbx_browsers_current_text_changed(self, text: str):
        self.refresh_profiles(text)

        if text == "Chrome":
            self.ui.wg_tab_edge.setEnabled(False)
            self.ui.wg_tab_brave.setEnabled(False)
            self.ui.lb_edge_applicable.setVisible(True)
            self.ui.lb_brave_applicable.setVisible(True)
            self.ui.lb_edge_reminder.setVisible(False)
            self.ui.lb_brave_reminder.setVisible(False)
            change_color(self.ui.wg_tab_edge, QtCore.Qt.GlobalColor.darkGray)
            change_color(self.ui.wg_tab_brave, QtCore.Qt.GlobalColor.darkGray)
        elif text == "Edge":
            self.ui.wg_tab_edge.setEnabled(True)
            self.ui.wg_tab_brave.setEnabled(False)
            self.ui.lb_edge_applicable.setVisible(False)
            self.ui.lb_brave_applicable.setVisible(True)
            self.ui.lb_edge_reminder.setVisible(True)
            self.ui.lb_brave_reminder.setVisible(False)
            change_color(self.ui.wg_tab_edge, QtCore.Qt.GlobalColor.black)
            change_color(self.ui.wg_tab_brave, QtCore.Qt.GlobalColor.darkGray)
        elif text == "Brave":
            self.ui.wg_tab_edge.setEnabled(False)
            self.ui.wg_tab_brave.setEnabled(True)
            self.ui.lb_edge_applicable.setVisible(True)
            self.ui.lb_brave_applicable.setVisible(False)
            self.ui.lb_edge_reminder.setVisible(False)
            self.ui.lb_brave_reminder.setVisible(True)
            change_color(self.ui.wg_tab_edge, QtCore.Qt.GlobalColor.darkGray)
            change_color(self.ui.wg_tab_brave, QtCore.Qt.GlobalColor.black)

    @staticmethod
    def _get_browser_profiles(browser: str) -> tuple[list, dict] | tuple[None, None]:
        lst_db = get_local_state_db(browser)
        profiles_dic = get_with_chained_keys(lst_db, ["profile", "info_cache"])
        if profiles_dic is None:
            return None, None

        profiles = list(profiles_dic.keys())
        profiles.sort(key=lambda x: 0 if x == "Default" else int(x.split(" ")[1]))

        return profiles, profiles_dic

    def refresh_profiles(self, browser: str):
        profiles, _ = self._get_browser_profiles(browser)
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

        # =============== Edge ======================

        if browser == "Edge":
            self._update_check_box(
                self.ui.cbx_edge_rewards,
                get_with_chained_keys(pref_db, ["edge_rewards", "show"]), True)
            self._update_check_box(
                self.ui.cbx_edge_custom_data,
                get_with_chained_keys(pref_db, ["autofill", "custom_data_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_wallet_checkout,
                get_with_chained_keys(pref_db, ["edge_wallet", "wallet_checkout_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_ec_browsing_history,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "browsing_history"]), False)
            self._update_check_box(
                self.ui.cbx_edge_ec_download_history,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "download_history"]), False)
            self._update_check_box(
                self.ui.cbx_edge_ec_cookies,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "cookies"]), False)
            self._update_check_box(
                self.ui.cbx_edge_ec_cache,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "cache"]), False)
            self._update_check_box(
                self.ui.cbx_edge_ec_passwords,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "passwords"]), False)
            self._update_check_box(
                self.ui.cbx_edge_ec_form_data,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "form_data"]), False)
            self._update_check_box(
                self.ui.cbx_edge_ec_site_settings,
                get_with_chained_keys(pref_db, ["browser", "clear_data_on_exit", "site_settings"]), False)
            self._update_check_box(
                self.ui.cbx_edge_personal_data,
                get_with_chained_keys(pref_db, ["user_experience_metrics", "personalization_data_consent_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_nav_err,
                get_with_chained_keys(pref_db, ["resolve_navigation_errors_use_web_service", "enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_alt_err,
                get_with_chained_keys(pref_db, ["alternate_error_pages", "enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_shopping_assist,
                get_with_chained_keys(pref_db, ["edge_shopping_assistant_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_follow,
                get_with_chained_keys(pref_db, ["edge_follow_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_follow_notif,
                get_with_chained_keys(pref_db, ["edge_follow_notification_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_tipping_assist,
                get_with_chained_keys(pref_db, ["edge_tipping_assistant_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_under_trig,
                get_with_chained_keys(pref_db, ["edge_underside_triggering_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_edge_tab_services,
                get_with_chained_keys(pref_db, ["edge_tab_services_enabled"]), True)

        # =============== Brave ======================

        elif browser == "Brave":
            self._update_check_box(
                self.ui.cbx_brave_news,
                get_with_chained_keys(pref_db, ["brave", "today", "should_show_toolbar_button"]), True)
            self._update_check_box(
                self.ui.cbx_brave_vpn,
                get_with_chained_keys(pref_db, ["brave", "brave_vpn", "show_button"]), True)
            self._update_check_box(
                self.ui.cbx_brave_rewards,
                get_with_chained_keys(pref_db, ["brave", "rewards", "show_brave_rewards_button_in_location_bar"]), True)
            self._update_check_box(
                self.ui.cbx_brave_rewards_tip,
                get_with_chained_keys(pref_db, ["brave", "rewards", "inline_tip_buttons_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_brave_wallet,
                get_with_chained_keys(pref_db, ["brave", "wallet", "show_wallet_icon_on_toolbar"]), True)
            self._update_check_box(
                self.ui.cbx_brave_wayback,
                get_with_chained_keys(pref_db, ["brave", "wayback_machine_enabled"]), True)
            self._update_check_box(
                self.ui.cbx_brave_cd_browsing_history,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "browsing_history_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_cache,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "cache_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_cookies,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "cookies_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_download_history,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "download_history_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_form_data,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "form_data_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_hosted_apps_data,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "hosted_apps_data_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_passwords,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "passwords_on_exit"]), False)
            self._update_check_box(
                self.ui.cbx_brave_cd_site_settings,
                get_with_chained_keys(pref_db, ["browser", "clear_data", "site_settings_on_exit"]), False)

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
            is_current=True,
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
            # --- Edge ----
            edge_rewards=self.ui.cbx_edge_rewards.checkState() == QtCore.Qt.CheckState.Checked,
            edge_custom_data=self.ui.cbx_edge_custom_data.checkState() == QtCore.Qt.CheckState.Checked,
            edge_wallet_checkout=self.ui.cbx_edge_wallet_checkout.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_browsing_history=self.ui.cbx_edge_ec_browsing_history.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_download_history=self.ui.cbx_edge_ec_download_history.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_cookies=self.ui.cbx_edge_ec_cookies.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_cache=self.ui.cbx_edge_ec_cache.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_passwords=self.ui.cbx_edge_ec_passwords.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_form_data=self.ui.cbx_edge_ec_form_data.checkState() == QtCore.Qt.CheckState.Checked,
            edge_ec_site_settings=self.ui.cbx_edge_ec_site_settings.checkState() == QtCore.Qt.CheckState.Checked,
            edge_personal_data=self.ui.cbx_edge_personal_data.checkState() == QtCore.Qt.CheckState.Checked,
            edge_nav_err=self.ui.cbx_edge_nav_err.checkState() == QtCore.Qt.CheckState.Checked,
            edge_alt_err=self.ui.cbx_edge_alt_err.checkState() == QtCore.Qt.CheckState.Checked,
            edge_shopping_assist=self.ui.cbx_edge_shopping_assist.checkState() == QtCore.Qt.CheckState.Checked,
            edge_follow=self.ui.cbx_edge_follow.checkState() == QtCore.Qt.CheckState.Checked,
            edge_follow_notif=self.ui.cbx_edge_follow_notif.checkState() == QtCore.Qt.CheckState.Checked,
            edge_tipping_assist=self.ui.cbx_edge_tipping_assist.checkState() == QtCore.Qt.CheckState.Checked,
            edge_under_trig=self.ui.cbx_edge_under_trig.checkState() == QtCore.Qt.CheckState.Checked,
            edge_tab_services=self.ui.cbx_edge_tab_services.checkState() == QtCore.Qt.CheckState.Checked,
            # --- Brave ----
            brave_news=self.ui.cbx_brave_news.checkState() == QtCore.Qt.CheckState.Checked,
            brave_vpn=self.ui.cbx_brave_vpn.checkState() == QtCore.Qt.CheckState.Checked,
            brave_rewards=self.ui.cbx_brave_rewards.checkState() == QtCore.Qt.CheckState.Checked,
            brave_rewards_tip=self.ui.cbx_brave_rewards_tip.checkState() == QtCore.Qt.CheckState.Checked,
            brave_wallet=self.ui.cbx_brave_wallet.checkState() == QtCore.Qt.CheckState.Checked,
            brave_wayback=self.ui.cbx_brave_wayback.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_browsing_history=self.ui.cbx_brave_cd_browsing_history.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_cache=self.ui.cbx_brave_cd_cache.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_cookies=self.ui.cbx_brave_cd_cookies.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_download_history=self.ui.cbx_brave_cd_download_history.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_form_data=self.ui.cbx_brave_cd_form_data.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_hosted_app_data=self.ui.cbx_brave_cd_hosted_apps_data.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_passwords=self.ui.cbx_brave_cd_passwords.checkState() == QtCore.Qt.CheckState.Checked,
            brave_cd_site_settings=self.ui.cbx_brave_cd_site_settings.checkState() == QtCore.Qt.CheckState.Checked,
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
        profiles, _ = self._get_browser_profiles(browser)

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
        # --- Edge ----
        edge_rewards = self.ui.cbx_edge_rewards.checkState() == QtCore.Qt.CheckState.Checked
        edge_custom_data = self.ui.cbx_edge_custom_data.checkState() == QtCore.Qt.CheckState.Checked
        edge_wallet_checkout = self.ui.cbx_edge_wallet_checkout.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_browsing_history = self.ui.cbx_edge_ec_browsing_history.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_download_history = self.ui.cbx_edge_ec_download_history.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_cookies = self.ui.cbx_edge_ec_cookies.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_cache = self.ui.cbx_edge_ec_cache.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_passwords = self.ui.cbx_edge_ec_passwords.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_form_data = self.ui.cbx_edge_ec_form_data.checkState() == QtCore.Qt.CheckState.Checked
        edge_ec_site_settings = self.ui.cbx_edge_ec_site_settings.checkState() == QtCore.Qt.CheckState.Checked
        edge_personal_data = self.ui.cbx_edge_personal_data.checkState() == QtCore.Qt.CheckState.Checked
        edge_nav_err = self.ui.cbx_edge_nav_err.checkState() == QtCore.Qt.CheckState.Checked
        edge_alt_err = self.ui.cbx_edge_alt_err.checkState() == QtCore.Qt.CheckState.Checked
        edge_shopping_assist = self.ui.cbx_edge_shopping_assist.checkState() == QtCore.Qt.CheckState.Checked
        edge_follow = self.ui.cbx_edge_follow.checkState() == QtCore.Qt.CheckState.Checked
        edge_follow_notif = self.ui.cbx_edge_follow_notif.checkState() == QtCore.Qt.CheckState.Checked
        edge_tipping_assist = self.ui.cbx_edge_tipping_assist.checkState() == QtCore.Qt.CheckState.Checked
        edge_under_trig = self.ui.cbx_edge_under_trig.checkState() == QtCore.Qt.CheckState.Checked
        edge_tab_services = self.ui.cbx_edge_tab_services.checkState() == QtCore.Qt.CheckState.Checked
        # --- Brave ----
        brave_news = self.ui.cbx_brave_news.checkState() == QtCore.Qt.CheckState.Checked
        brave_vpn = self.ui.cbx_brave_vpn.checkState() == QtCore.Qt.CheckState.Checked
        brave_rewards = self.ui.cbx_brave_rewards.checkState() == QtCore.Qt.CheckState.Checked
        brave_rewards_tip = self.ui.cbx_brave_rewards_tip.checkState() == QtCore.Qt.CheckState.Checked
        brave_wallet = self.ui.cbx_brave_wallet.checkState() == QtCore.Qt.CheckState.Checked
        brave_wayback = self.ui.cbx_brave_wayback.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_browsing_history = self.ui.cbx_brave_cd_browsing_history.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_cache = self.ui.cbx_brave_cd_cache.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_cookies = self.ui.cbx_brave_cd_cookies.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_download_history = self.ui.cbx_brave_cd_download_history.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_form_data = self.ui.cbx_brave_cd_form_data.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_hosted_app_data = self.ui.cbx_brave_cd_hosted_apps_data.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_passwords = self.ui.cbx_brave_cd_passwords.checkState() == QtCore.Qt.CheckState.Checked
        brave_cd_site_settings = self.ui.cbx_brave_cd_site_settings.checkState() == QtCore.Qt.CheckState.Checked

        for profile in profiles:
            is_current = profile == cur_profile

            self.apply_one_profile_settings(
                browser, profile,
                is_current=is_current,
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
                # --- Edge ---
                edge_rewards=edge_rewards,
                edge_custom_data=edge_custom_data,
                edge_wallet_checkout=edge_wallet_checkout,
                edge_ec_browsing_history=edge_ec_browsing_history,
                edge_ec_download_history=edge_ec_download_history,
                edge_ec_cookies=edge_ec_cookies,
                edge_ec_cache=edge_ec_cache,
                edge_ec_passwords=edge_ec_passwords,
                edge_ec_form_data=edge_ec_form_data,
                edge_ec_site_settings=edge_ec_site_settings,
                edge_personal_data=edge_personal_data,
                edge_nav_err=edge_nav_err,
                edge_alt_err=edge_alt_err,
                edge_shopping_assist=edge_shopping_assist,
                edge_follow=edge_follow,
                edge_follow_notif=edge_follow_notif,
                edge_tipping_assist=edge_tipping_assist,
                edge_under_trig=edge_under_trig,
                edge_tab_services=edge_tab_services,
                # --- Brave ---
                brave_news=brave_news,
                brave_vpn=brave_vpn,
                brave_rewards=brave_rewards,
                brave_rewards_tip=brave_rewards_tip,
                brave_wallet=brave_wallet,
                brave_wayback=brave_wayback,
                brave_cd_browsing_history=brave_cd_browsing_history,
                brave_cd_cache=brave_cd_cache,
                brave_cd_cookies=brave_cd_cookies,
                brave_cd_download_history=brave_cd_download_history,
                brave_cd_form_data=brave_cd_form_data,
                brave_cd_hosted_app_data=brave_cd_hosted_app_data,
                brave_cd_passwords=brave_cd_passwords,
                brave_cd_site_settings=brave_cd_site_settings,
            )

            if is_current:
                self.update_profile_settings(browser, profile)

        QtWidgets.QMessageBox.information(
            self, "提示",
            f"{browser} 的所有用户 已应用当前设置。"
        )

    def apply_one_profile_settings(
            self, browser: str, profile: str, *, is_current: bool,
            save_pass: bool, auto_signin: bool, save_card: bool, save_addr: bool,
            make_payment: bool, not_track: bool, clear_cookies: bool, forbid_location: bool,
            clear_browser_engines: bool, clear_saved_pass: bool,
            # --- Edge ---
            edge_rewards: bool, edge_custom_data: bool, edge_wallet_checkout: bool,
            edge_ec_browsing_history: bool, edge_ec_download_history: bool,
            edge_ec_cookies: bool, edge_ec_cache: bool, edge_ec_passwords: bool,
            edge_ec_form_data: bool, edge_ec_site_settings: bool,
            edge_personal_data: bool, edge_nav_err: bool, edge_alt_err: bool,
            edge_shopping_assist: bool, edge_follow: bool, edge_follow_notif: bool,
            edge_tipping_assist: bool, edge_under_trig: bool, edge_tab_services: bool,
            # --- Brave ---
            brave_news: bool, brave_vpn: bool, brave_rewards: bool,
            brave_rewards_tip: bool, brave_wallet: bool, brave_wayback: bool,
            brave_cd_browsing_history: bool, brave_cd_cache: bool,
            brave_cd_cookies: bool, brave_cd_download_history: bool,
            brave_cd_form_data: bool, brave_cd_hosted_app_data: bool,
            brave_cd_passwords: bool, brave_cd_site_settings: bool,
    ):
        pref_db = get_preferences_db(browser, profile)

        chrome_settings = {
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
        append_dictionary(pref_db, chrome_settings)

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

        # ============= Edge ===================

        if browser == "Edge":
            edge_settings = {
                "edge_rewards": {
                    "show": edge_rewards,
                },
                "autofill": {
                    "autostuff_enabled": save_addr,  # 这里设置为等同 保存并填充“基本信息”
                    "custom_data_enabled": edge_custom_data,
                },
                "edge_wallet": {
                    "wallet_checkout_enabled": edge_wallet_checkout,
                },
                "browser": {
                    "clear_data_on_exit": {
                        "browsing_history": edge_ec_browsing_history,
                        "download_history": edge_ec_download_history,
                        "cookies": edge_ec_cookies,
                        "cache": edge_ec_cache,
                        "passwords": edge_ec_passwords,
                        "form_data": edge_ec_form_data,
                        "site_settings": edge_ec_site_settings,
                    },
                },
                "user_experience_metrics": {
                    "personalization_data_consent_enabled": edge_personal_data,
                },
                "resolve_navigation_errors_use_web_service": {
                    "enabled": edge_nav_err,
                },
                "alternate_error_pages": {
                    "enabled": edge_alt_err,
                },
                "edge_shopping_assistant_enabled": edge_shopping_assist,
                "edge_follow_enabled": edge_follow,
                "edge_follow_notification_enabled": edge_follow_notif,
                "edge_tipping_assistant_enabled": edge_tipping_assist,
                "edge_underside_triggering_enabled": edge_under_trig,
                "edge_tab_services_enabled": edge_tab_services,
            }

            append_dictionary(pref_db, edge_settings)

        # ============= Brave ===================

        elif browser == "Brave":
            brave_settings = {
                "brave": {
                    "today": {
                        "should_show_toolbar_button": brave_news,
                    },
                    "brave_vpn": {
                        "show_button": brave_vpn,
                    },
                    "rewards": {
                        "show_brave_rewards_button_in_location_bar": brave_rewards,
                        "inline_tip_buttons_enabled": brave_rewards_tip,
                    },
                    "wallet": {
                        "show_wallet_icon_on_toolbar": brave_wallet,
                    },
                    "wayback_machine_enabled": brave_wayback,
                },
                "browser": {
                    "clear_data": {
                        "browsing_history_on_exit": brave_cd_browsing_history,
                        "cache_on_exit": brave_cd_cache,
                        "cookies_on_exit": brave_cd_cookies,
                        "download_history_on_exit": brave_cd_download_history,
                        "form_data_on_exit": brave_cd_form_data,
                        "hosted_apps_data_on_exit": brave_cd_hosted_app_data,
                        "passwords_on_exit": brave_cd_passwords,
                        "site_settings_on_exit": brave_cd_site_settings,
                    },
                }
            }

            append_dictionary(pref_db, brave_settings)

        overwrite_preferences_db(pref_db, browser, profile)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
