# code: utf8
import os
import json
import sys
from pathlib import Path


def _enter_level(data: dict, bmx_db: dict, profile_name: str, pos: list[str, ...]):

    if data["type"] == "url":
        url = data["url"]
        name = data["name"]
        if url not in bmx_db:
            bmx_db[url] = {}
        ext_info = bmx_db[url]
        ext_info["name"] = name
        if "profiles_pos" not in ext_info:
            ext_info["profiles_pos"] = []
        ext_info["profiles_pos"].append((profile_name, "/".join(pos)))

        return
    elif data["type"] == "folder":
        pos = pos.copy()
        pos.append(data["name"])
        for child in data["children"]:
            _enter_level(child, bmx_db, profile_name, pos)
    else:
        return


def _handle_single_profile(profile_path: Path, bmx_db: dict[str, dict]):
    bookmarks_path = Path(profile_path, "Bookmarks")
    if not bookmarks_path.exists():
        return

    with open(bookmarks_path, "r", encoding="utf8") as f:
        data = json.load(f)  # type: dict

    if "roots" not in data:
        return

    roots = data["roots"]
    for folder in roots:
        pos = [""]
        _enter_level(roots[folder], bmx_db, profile_path.name, pos)


def scan_bookmarks(browser: str) -> tuple[dict[str, dict], dict[str, str]]:
    bmx_db = {}  # type: dict[str, dict]
    plat = sys.platform
    user_path = os.path.expanduser("~")
    if browser == "Chrome":
        if plat == "win32":
            data_path = Path(user_path, "AppData", "Local", "Google", "Chrome", "User Data")
        elif plat == "darwin":
            data_path = Path(user_path, "Library", "Application Support", "Google", "Chrome")
        else:
            return {}, {}
    elif browser == "Edge":
        if plat == "win32":
            data_path = Path(user_path, "AppData", "Local", "Microsoft", "Edge", "User Data")
        elif plat == "darwin":
            data_path = Path(user_path, "Library", "Application Support", "Microsoft Edge")
        else:
            return {}, {}
    elif browser == "Brave":
        if plat == "win32":
            data_path = Path(user_path, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data")
        elif plat == "darwin":
            data_path = Path(user_path, "Library", "Application Support", "BraveSoftware", "Brave-Browser")
        else:
            return {}, {}
    else:
        return {}, {}

    if not data_path.exists():
        return {}, {}

    profile_paths = []
    profile_def = Path(data_path, "Default")
    if profile_def.exists():
        profile_paths.append(profile_def)
    profile_paths.extend(data_path.glob(r"Profile [0-9]*"))

    for p in profile_paths:
        _handle_single_profile(p, bmx_db)

    return bmx_db, {bmx_db[k]["name"]: k for k in bmx_db}
