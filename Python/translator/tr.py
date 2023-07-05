# code: utf8

# Change log
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

version = (1, 0, 20230705)

_dictionary = {}  # type: dict[str, dict[str, str]]
_locale = ""


def tr_init(filename: str | PathLike, locale: str):
    global _dictionary, _locale

    _locale = locale
    try:
        with open(filename, "r", encoding="utf8") as fd:
            _dictionary = json.load(fd)
    except (json.JSONDecodeError, FileNotFoundError):
        warnings.warn("Failed to load dictionary. tr() will not work")


def tr(key: str, locale: str | None = None) -> str:
    if locale is None:
        locale = _locale

    if key not in _dictionary:
        return key

    if locale not in _dictionary[key]:
        return key

    return _dictionary[key][locale]
