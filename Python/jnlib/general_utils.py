# code: utf8
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


def decimal2any(num: int, base: int, big_endian: bool = False) -> tuple[int, ...]:
    res = []  # type: list[int, ...]
    while True:
        div, mod = divmod(num, base)
        res.append(mod)
        if div == 0:
            break
        num = div
    if big_endian:
        res = res[::-1]
    return tuple(res)


def any2decimal(num: tuple[int, ...], base: int, big_endian: bool = False) -> int:
    res = 0
    if big_endian:
        num = num[::-1]
    for i in range(len(num)):
        res += num[i] * pow(base, i)
    return res
