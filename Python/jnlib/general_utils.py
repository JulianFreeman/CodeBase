# code: utf8
from pathlib import Path


def args_match(args: tuple, count: int, a_types: tuple) -> bool:
    if len(args) != count:
        return False

    for ori, exp in zip(args, a_types):
        if not isinstance(ori, exp):
            return False

    return True


def get_with_chained_keys(dic: dict, keys: list):
    k = keys[0]
    if k not in dic:
        return None
    if len(keys) == 1:
        return dic[k]
    return get_with_chained_keys(dic[k], keys[1:])


def append_dic(dic: dict, sub_dic: dict):
    for k in sub_dic:
        if not ((k in dic and isinstance(dic[k], dict)) and isinstance(sub_dic[k], dict)):
            dic[k] = sub_dic[k]
            continue

        append_dic(dic[k], sub_dic[k])


def path_not_exist(path: str | Path) -> bool:
    if isinstance(path, str):
        return len(path) == 0 or not Path(path).exists()
    elif isinstance(path, Path):
        return not path.exists()
    else:
        return True
