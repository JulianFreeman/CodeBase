# code: utf8
import json
import shutil
from os import PathLike
from pathlib import Path
from PySide6 import QtCore

from jnlib.chromium_utils import (
    get_data_path, get_local_state_db,
    get_with_chained_keys,
    get_profile_paths,
    get_secure_preferences_db,
    overwrite_secure_preferences_db,
    get_preferences_db,
    overwrite_preferences_db,
    get_x_in_profile_path,
)


def _read_plg_db() -> dict[str, dict]:
    settings = QtCore.QSettings()
    plg_db = settings.value("plg_db", "")  # type: str | object
    if len(plg_db) == 0 or not Path(plg_db).exists():
        return {}

    try:
        with open(plg_db, "r", encoding="utf8") as f:
            data = json.load(f)
    except:
        return {}
    else:
        return data


def _get_largest_icon(icons: dict, prefix_path: str | PathLike) -> str:
    if len(icons) != 0:
        icon_path = icons[str(max(map(int, icons.keys())))]  # type: str
        # 以 / 为开头会导致前面的路径被忽略
        if icon_path.startswith("/"):
            icon_path = icon_path[1:]
        icon_p = Path(prefix_path, icon_path)
        if icon_p.exists():
            icon = str(icon_p)
        else:
            icon = ""
    else:
        icon = ""

    return icon


def _get_info_from_manifest(ext_path: Path) -> tuple[str, str]:
    """
    ext_path 下应该包含 manifest.json 文件
    """
    manifest_path = Path(ext_path, "manifest.json")
    if not manifest_path.exists():
        return "", ""

    with open(manifest_path, "r", encoding="utf8") as f:
        data = json.load(f)  # type: dict

    name = data.get("name", "").replace("/", "").replace("\\", "")
    icons = data.get("icons", {})
    icon = _get_largest_icon(icons, ext_path)

    return name, icon


def _handle_single_profile(browser: str, profile_path: Path, ext_db: dict[str, dict],
                           plg_db: dict[str, dict], lst_db: dict):
    extension_path = Path(profile_path, "Extensions")
    if not extension_path.exists():
        return

    profile_id = profile_path.name

    profile_name = get_with_chained_keys(lst_db, ["profile", "info_cache", profile_id, "shortcut_name"])
    if profile_name is None:
        profile_name = get_with_chained_keys(lst_db, ["profile", "info_cache", profile_id, "name"])
    if profile_name is None:
        profile_name = ""

    s_pref_db = get_secure_preferences_db(browser, profile_id)
    ext_settings = get_with_chained_keys(s_pref_db, ["extensions", "settings"])  # type: dict[str, dict]
    if ext_settings is None:
        return

    for ext_id in ext_settings:
        ext_data = ext_settings[ext_id]
        if "manifest" in ext_data:
            manifest = ext_data["manifest"]  # type: dict
            # 有 manifest 的话一定有 path，应该吧
            path = ext_data["path"]  # type: str
            if path.startswith(ext_id):
                path_p = Path(extension_path, path)
            else:
                path_p = Path(path)
            # 有些插件的路径是不存在的，可能真的不存在，或者插件不可见
            if not path_p.exists():
                continue
            name = manifest.get("name", "").replace("/", "").replace("\\", "")
            icon = _get_largest_icon(manifest.get("icons", {}), path_p)
        elif "path" in ext_data:
            path = ext_data["path"]
            path_p = Path(path)
            if not path_p.exists():
                continue
            name, icon = _get_info_from_manifest(path_p)
        else:
            continue

        safe = None
        note = ""

        if ext_id not in ext_db:
            ext_db.setdefault(ext_id, {})

        ext_info = ext_db[ext_id]

        if ext_id in plg_db:
            name = plg_db[ext_id].get("name", name)
            safe = plg_db[ext_id].get("safe", safe)
            note = plg_db[ext_id].get("note", note)

        ext_info["name"] = name
        ext_info["icon"] = icon
        ext_info["safe"] = safe
        ext_info["note"] = note

        if "profiles" not in ext_info:
            ext_info.setdefault("profiles", [])

        p_id_name = f"{profile_id}%{profile_name}"
        if p_id_name not in ext_info["profiles"]:
            ext_info["profiles"].append(p_id_name)


def scan_extensions(browser: str) -> dict[str, dict]:
    ext_db = {}  # type: dict[str, dict]

    data_path = get_data_path(browser)
    if not data_path.exists():
        return {}

    lst_db = get_local_state_db(browser, data_path=data_path)
    profile_paths = get_profile_paths(browser, data_path=data_path)

    plg_db = _read_plg_db()

    for profile in profile_paths:
        _handle_single_profile(browser, profile, ext_db, plg_db, lst_db)

    return ext_db


def delete_extension(browser: str, profile: str, ids: str) -> bool:
    # 先把文件夹删了
    extensions_path = get_x_in_profile_path(browser, profile, "Extensions")
    if extensions_path is not None:
        ext_folder_path = Path(extensions_path, ids)
        if ext_folder_path.exists():
            shutil.rmtree(ext_folder_path, ignore_errors=True)

    s_pref_db = get_secure_preferences_db(browser, profile)
    ext_settings = get_with_chained_keys(s_pref_db, ["extensions", "settings"])  # type: dict
    if ext_settings is None or ids not in ext_settings:
        return False
    ext_settings.pop(ids)
    overwrite_secure_preferences_db(s_pref_db, browser, profile)

    # 其实上面如果删除成功了，下面的也无所谓了，所以不管如何返回都是 True

    pref_db = get_preferences_db(browser, profile)
    pinned_ext = get_with_chained_keys(pref_db, ["extensions", "pinned_extensions"])  # type: list
    if pinned_ext is None or ids not in pinned_ext:
        return True
    pinned_ext.remove(ids)
    overwrite_preferences_db(pref_db, browser, profile)

    return True
