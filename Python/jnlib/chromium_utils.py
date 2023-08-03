# code: utf8
import os
import sys
import json
from pathlib import Path

from jnlib.general_utils import get_with_chained_keys


PLAT = sys.platform
USER_PATH = os.path.expanduser("~")
DATA_PATH_MAP = {
    "win32": {
        "Chrome": Path(USER_PATH, "AppData", "Local", "Google", "Chrome", "User Data"),
        "Edge": Path(USER_PATH, "AppData", "Local", "Microsoft", "Edge", "User Data"),
        "Brave": Path(USER_PATH, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data"),
    },
    "darwin": {
        "Chrome": Path(USER_PATH, "Library", "Application Support", "Google", "Chrome"),
        "Edge": Path(USER_PATH, "Library", "Application Support", "Microsoft Edge"),
        "Brave": Path(USER_PATH, "Library", "Application Support", "BraveSoftware", "Brave-Browser"),
    },
}
EXEC_PATH_MAP = {
    "win32": {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    },
    "darwin": {
        "chrome": r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "edge": r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "brave": r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    },
}


def get_exec_path(browser: str) -> Path | None:
    exec_path = get_with_chained_keys(EXEC_PATH_MAP, [PLAT, browser])  # type: str
    if exec_path is None:
        return None
    exec_path_p = Path(exec_path)
    if not exec_path_p.exists():
        return None

    return exec_path_p


def get_data_path(browser: str) -> Path | None:
    data_path = get_with_chained_keys(DATA_PATH_MAP, [PLAT, browser])  # type: Path | None
    if data_path is None or not data_path.exists():
        return None

    return data_path


def get_x_in_profile_path(browser: str, profile: str, x: str, *, data_path: Path | None = None) -> Path | None:
    if data_path is None:
        data_path = get_data_path(browser)
    if data_path is None:
        return None

    x_path = Path(data_path, profile, x)
    if not x_path.exists():
        return None

    return x_path


def get_preferences_path(browser: str, profile: str) -> Path | None:
    preferences_path = get_x_in_profile_path(browser, profile, "Preferences")
    if preferences_path is None:
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


def get_secure_preferences_path(browser: str, profile: str) -> Path | None:
    secure_pref_path = get_x_in_profile_path(browser, profile, "Secure Preferences")
    if secure_pref_path is None:
        return None

    return secure_pref_path


def get_secure_preferences_db(browser: str, profile: str) -> dict:
    secure_pref_path = get_secure_preferences_path(browser, profile)
    if secure_pref_path is None:
        return {}

    with open(secure_pref_path, "r", encoding="utf8") as f:
        s_pref_db = json.load(f)

    return s_pref_db


def overwrite_secure_preferences_db(new_s_pref_db: dict, browser: str, profile: str) -> bool:
    secure_pref_path = get_secure_preferences_path(browser, profile)
    if secure_pref_path is None:
        return False

    with open(secure_pref_path, "w", encoding="utf8") as f:
        json.dump(new_s_pref_db, f)

    return True


def get_local_state_db(browser: str, *, data_path: Path | None = None) -> dict:
    if data_path is None:
        data_path = get_data_path(browser)
    if data_path is None:
        return {}

    local_state_path = Path(data_path, "Local State")
    if not local_state_path.exists():
        return {}

    with open(local_state_path, "r", encoding="utf8") as f:
        lst_db = json.load(f)

    return lst_db


def get_profile_paths(browser: str, *, data_path: Path | None = None) -> list[Path]:
    if data_path is None:
        data_path = get_data_path(browser)
    if data_path is None:
        return []

    lst_db = get_local_state_db(browser, data_path=data_path)
    info_cache = get_with_chained_keys(lst_db, ["profile", "info_cache"])  # type: dict
    if info_cache is None:
        profile_paths = []
    else:
        profile_paths = [Path(data_path, p) for p in info_cache]

    return profile_paths
