# code: utf8
import os
import json
import sys
from pathlib import Path
from PySide6 import QtCore


# 此文件中
# ext_db 是现扫描的插件数据
# plg_db 是预存的插件数据
# 有点乱，但先这样吧


def _read_plg_db() -> dict:
    settings = QtCore.QSettings("JnPrograms", "BPC")
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


def _handle_single_extension(extension_path: Path, profile_id: str, profile_name: str,
                             ext_db: dict[str, dict], plg_db: dict):
    ext_id = extension_path.name

    for version_path in extension_path.glob("*"):
        if not version_path.is_dir():
            continue

        manifest_path = Path(version_path, "manifest.json")
        if not manifest_path.exists():
            continue

        with open(manifest_path, "r", encoding="utf8") as f:
            data = json.load(f)  # type: dict

        name = data.get("name", "").replace("/", "").replace("\\", "")
        icons = data.get("icons", {})
        if len(icons) != 0:
            icon_p = Path(version_path, icons[str(max(map(int, icons.keys())))])
            if icon_p.exists():
                icon = str(icon_p)
            else:
                icon = ""
        else:
            icon = ""
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

        ext_info["profiles"].append(f"{profile_id}%{profile_name}")


def _handle_single_profile(profile_path: Path, ext_db: dict[str, dict], plg_db: dict, lst_db: dict):
    extension_path = Path(profile_path, "Extensions")
    if not extension_path.exists():
        return

    profile_id = profile_path.name

    try:
        profile_name = lst_db["profile"]["info_cache"][profile_id]["shortcut_name"]
    except KeyError:
        preferences_path = Path(profile_path, "Preferences")
        if preferences_path.exists():
            with open(preferences_path, "r", encoding="utf8") as f:
                pref = json.load(f)
            if "profile" in pref and "name" in pref["profile"]:
                profile_name = pref["profile"]["name"]
            else:
                profile_name = ""
        else:
            profile_name = ""

    for e in extension_path.glob("*"):
        _handle_single_extension(e, profile_id, profile_name, ext_db, plg_db)


def scan_google_plugins(browser: str) -> dict[str, dict]:
    ext_db = {}  # type: dict[str, dict]
    plat = sys.platform
    user_path = os.path.expanduser("~")
    if browser == "Chrome":
        if plat == "win32":
            data_path = Path(user_path, "AppData", "Local", "Google", "Chrome", "User Data")
        elif plat == "darwin":
            data_path = Path(user_path, "Library", "Application Support", "Google", "Chrome")
        else:
            return {}
    elif browser == "Edge":
        if plat == "win32":
            data_path = Path(user_path, "AppData", "Local", "Microsoft", "Edge", "User Data")
        elif plat == "darwin":
            data_path = Path(user_path, "Library", "Application Support", "Microsoft Edge")
        else:
            return {}
    elif browser == "Brave":
        if plat == "win32":
            data_path = Path(user_path, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data")
        elif plat == "darwin":
            data_path = Path(user_path, "Library", "Application Support", "BraveSoftware", "Brave-Browser")
        else:
            return {}
    else:
        return {}

    if not data_path.exists():
        return {}

    local_state_path = Path(data_path, "Local State")
    if not local_state_path.exists():
        lst_db = {}
    else:
        with open(local_state_path, "r", encoding="utf8") as f:
            lst_db = json.load(f)

    profile_paths = []
    profile_def = Path(data_path, "Default")
    if profile_def.exists():
        profile_paths.append(profile_def)
    profile_paths.extend(data_path.glob(r"Profile [0-9]*"))

    plg_db = _read_plg_db()

    for p in profile_paths:
        _handle_single_profile(p, ext_db, plg_db, lst_db)

    return ext_db
