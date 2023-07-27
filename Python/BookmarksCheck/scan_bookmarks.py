# code: utf8
import os
import json
import sys
from pathlib import Path


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
    data_path = get_with_chained_keys(_DATA_PATH_MAP, [_PLAT, browser])
    if data_path is None or not data_path.exists():
        return {}, {}

    profile_paths = []
    profile_def = Path(data_path, "Default")
    if profile_def.exists():
        profile_paths.append(profile_def)
    profile_paths.extend(data_path.glob(r"Profile [0-9]*"))

    for p in profile_paths:
        _handle_single_profile(p, bmx_db)

    return bmx_db, {bmx_db[k]["name"]: k for k in bmx_db}


def delete_bookmark(browser: str, profile: str, url: str) -> tuple[bool, int]:
    data_path = get_with_chained_keys(_DATA_PATH_MAP, [_PLAT, browser])
    if data_path is None or not data_path.exists():
        return False, 3
    profile_p = Path(data_path, profile)
    if not profile_p.exists():
        return False, 1
    bookmark_bak_p = Path(profile_p, "Bookmarks.bak")
    if bookmark_bak_p.exists():
        os.remove(bookmark_bak_p)
    bookmark_p = Path(profile_p, "Bookmarks")
    if not bookmark_p.exists():
        return False, 2

    with open(bookmark_p, "r", encoding="utf8") as f:
        bm_db = json.load(f)  # type: dict
    if "checksum" in bm_db:
        bm_db.pop("checksum")

    def search_and_delete(data: dict, parent: list) -> bool:
        match data["type"]:
            case "url":
                if data["url"] == url:
                    parent.remove(data)
                    return True
                else:
                    return False
            case "folder":
                children = data["children"]
                i = 0
                while i < len(children):
                    is_deleted = search_and_delete(children[i], children)
                    if not is_deleted:
                        i += 1
            case _:
                return False

    root = bm_db["roots"]
    for f in root:
        search_and_delete(root[f], [])

    with open(bookmark_p, "w", encoding="utf8") as f:
        json.dump(bm_db, f, indent=4, ensure_ascii=False)

    return True, 0
