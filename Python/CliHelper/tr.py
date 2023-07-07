# code: utf8

# Change log
#
# v1.1
# 1. 添加 tr_set
#
# v1.0
# 初始版本
#

####################
#  _______ _____   #
# |__   __|  __ \  #
#    | |  | |__) | #
#    | |  |  _  /  #
#    | |  | | \ \  #
#    |_|  |_|  \_\ #
####################

import json
import warnings
from os import PathLike

version = (1, 1, 20230707)

_dictionary = {}  # type: dict[str, dict[str, str]]
_locale = "en_us"


lang_map = {
    "en_us": "English (US)",
    "zh_cn": "Simplified Chinese",
}


def tr_init(filename: str | PathLike, locale: str | None = None):
    global _dictionary, _locale

    if locale is not None:
        _locale = locale
    try:
        with open(filename, "r", encoding="utf8") as fd:
            _dictionary = json.load(fd)
    except (json.JSONDecodeError, FileNotFoundError):
        warnings.warn("Failed to load dictionary. tr() will not work")


def tr_set(locale: str):
    global _locale
    _locale = locale


def tr(key: str, locale: str | None = None) -> str:
    if locale is None:
        locale = _locale

    if key not in _dictionary:
        return key

    if locale not in _dictionary[key]:
        return key

    return _dictionary[key][locale]
