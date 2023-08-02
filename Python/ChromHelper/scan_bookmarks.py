# code: utf8
import os
import json
from pathlib import Path

from jnlib.chromium_utils import (
    get_data_path, get_profile_paths,
    get_x_in_profile_path,
)


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

    elif data["type"] == "folder":
        pos = pos.copy()
        pos.append(data["name"])
        for child in data["children"]:
            _enter_level(child, bmx_db, profile_name, pos)


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
    profile_paths = get_profile_paths(browser)

    for p in profile_paths:
        _handle_single_profile(p, bmx_db)

    return bmx_db, {bmx_db[k]["name"]: k for k in bmx_db}


def delete_bookmark(browser: str, profile: str, url: str) -> bool:
    data_path = get_data_path(browser)
    if data_path is None:
        return False
    bookmark_bak_p = get_x_in_profile_path(browser, profile, "Bookmarks.bak", data_path=data_path)
    if bookmark_bak_p is not None:
        os.remove(bookmark_bak_p)
    bookmark_p = get_x_in_profile_path(browser, profile, "Bookmarks", data_path=data_path)
    if bookmark_p is None:
        return False

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

    return True
