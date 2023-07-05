# coding: utf8
import json
import time
from os import PathLike
from pathlib import Path

from clihelper import CliHelper, request_input
from pyrsa import PyRSA
from genp import get_prime


BASE_PATH = Path(__file__).parent
PUBK_HEAD = b"PUBK"
PVTK_HEAD = b"PVTK"
ENCF_HEAD = b"ENCF"
CONFIG_FILENAME = "config.json"
REPO_FILENAME = "repo.json"
BLOCK_SIZE = 512


def _dec2any(num: int, base: int) -> tuple[int]:
    res = []
    while True:
        q, r = divmod(num, base)
        res.append(r)
        if q == 0:
            break
        num = q
    return tuple(res)


# def _any2dec(num: tuple[int], base: int) -> int:
#     res = 0
#     for i in range(len(num)):
#         res += num[i] * pow(base, i)
#     return res


def _read_keyfile(filepath: str | PathLike) -> tuple[int, int]:
    with open(filepath, "rb") as f:
        head = f.read(4)
        if head not in (PUBK_HEAD, PVTK_HEAD):
            return -1, -1
        ln_b1 = f.read(4)
        ln_b2 = f.read(4)
        ln_1 = int.from_bytes(ln_b1, "little")
        ln_2 = int.from_bytes(ln_b2, "little")
        first = f.read(ln_1)
        second = f.read(ln_2)
        return int.from_bytes(first, "little"), int.from_bytes(second, "little")


def _gen_pq(n: int):
    p = get_prime(n)
    q = get_prime(n)
    return p, q


def _is_file(path: str | PathLike):
    path = Path(path)
    return path.exists() and path.is_file()


def _is_dir(path: str | PathLike):
    path = Path(path)
    return path.exists() and path.is_dir()


def gen_new_keys():
    with open(Path(BASE_PATH, CONFIG_FILENAME), "r", encoding="utf8") as cf:
        config = json.load(cf)

    u_save_path, state = request_input(
        "\nEnter the path where to save the keys",
        "Please enter a valid path.",
        has_default_val=True,
        default_val=config.get("keys_save_path", BASE_PATH),
        check_func=_is_dir,
    )
    if state is False:
        return None
    u_save_path = Path(u_save_path)

    keys_name, state = request_input(
        "\nEnter the name for key files",
        has_default_val=True,
        default_val=config.get("keys_default_name", "key"),
    )
    if state is False:
        return None

    key_len, state = request_input(
        "\nEnter the key bit length",
        "It's not a digit.",
        has_default_val=True,
        default_val=config.get("key_bit_length", "1024"),
        check_func=lambda x: x.isdigit(),
    )
    if state is False:
        return None
    pq_len = abs(int(key_len)) // 2

    print("\nStart generating new keys...")
    st = time.time()
    p, q = _gen_pq(pq_len)
    rsa = PyRSA(p=p, q=q)
    rsa.set_valid_e()
    rsa.calc_d()
    pbk = rsa.get_public_key()
    pvk = rsa.get_private_key()
    ln_b256_n = len(_dec2any(pbk[0], 256))
    ln_b256_e = len(_dec2any(pbk[1], 256))
    ln_b256_d = len(_dec2any(pvk[1], 256))
    out_pbk = [
        PUBK_HEAD,
        ln_b256_n.to_bytes(4, "little"),
        ln_b256_e.to_bytes(4, "little"),
        pbk[0].to_bytes(ln_b256_n, "little"),
        pbk[1].to_bytes(ln_b256_e, "little")
    ]
    out_pvk = [
        PVTK_HEAD,
        ln_b256_n.to_bytes(4, "little"),
        ln_b256_d.to_bytes(4, "little"),
        pvk[0].to_bytes(ln_b256_n, "little"),
        pvk[1].to_bytes(ln_b256_d, "little")
    ]

    print("Writing new keys...")
    with open(Path(u_save_path, f"{keys_name}.pubk"), "wb") as f_pbk, \
         open(Path(u_save_path, f"{keys_name}.pvtk"), "wb") as f_pvk:
        f_pbk.write(b"".join(out_pbk))
        f_pvk.write(b"".join(out_pvk))

    print("Successfully generated new keys.")
    print(f"Time: {time.time() - st:.2f}s")


def load_key():
    load_path, state = request_input(
        "\nEnter the key path",
        "Invalid file path.",
        check_func=_is_file,
    )
    if state is False:
        return None
    load_path = Path(load_path)

    with open(load_path, "rb") as lf:
        head = lf.read(4)
    repo_path = Path(BASE_PATH, REPO_FILENAME)
    with open(repo_path, "r", encoding="utf8") as rf:
        repo = json.load(rf)  # type: dict

    if head in (PUBK_HEAD, PVTK_HEAD):
        th = "public" if head == PUBK_HEAD else "private"
        with open(repo_path, "w", encoding="utf8") as rf:
            ki = repo.get(th, [])
            if not isinstance(ki, list):
                ki = []
            ki.append(str(load_path))
            repo[th] = ki
            json.dump(repo, rf, indent=4)
        print(f"Added one {th} key: {load_path.name}")
    else:
        print("Not a key file.")


def encrypt_file():
    repo_path = Path(BASE_PATH, REPO_FILENAME)
    with open(repo_path, "r", encoding="utf8") as rf:
        repo = json.load(rf)  # type: dict
    public_keys = repo.get("public", [])
    ln_public_keys = len(public_keys)
    if ln_public_keys == 0:
        print("\nThere is no public keys stored.")
        return None

    print(f"\nThe stored public keys:")
    for i in range(ln_public_keys):
        print(f"{i:>{len(str(ln_public_keys))}}. [{public_keys[i]}]")

    opt, state = request_input(
        "\nChoose the public key you want to use to encrypt",
        "No such option.",
        check_func=lambda x: x.isdigit() and int(x) in range(ln_public_keys),
    )
    if state is False:
        return None

    pbk_f = public_keys[int(opt)]
    n, e = _read_keyfile(pbk_f)
    if n == -1 or e == -1:
        print("Not a valid key file.")
        return None

    rsa = PyRSA()
    rsa.set_public_key((n, e))

    tar_file, state = request_input(
        "\nEnter the file path you want to encrypt",
        "Invalid file path.",
        check_func=_is_file,
    )
    if state is False:
        return None
    tar_file = Path(tar_file)

    with open(tar_file, "rb") as tf:
        data = tf.read()

    print("\nStart encrypting...")
    st = time.time()

    last_blk_size = 0
    max_byte_size = 0
    enc_nums = []
    for i in range(0, len(data), BLOCK_SIZE):
        blk = data[i:i + BLOCK_SIZE]
        last_blk_size = len(blk)
        enc_num = rsa.encrypt(int.from_bytes(blk, "little"))
        size = len(_dec2any(enc_num, 256))
        enc_nums.append(enc_num)
        if size > max_byte_size:
            max_byte_size = size
    cont = b"".join(map(lambda x: x.to_bytes(max_byte_size, "little"), enc_nums))
    head = b"".join([
        ENCF_HEAD,
        max_byte_size.to_bytes(4, "little"),
        last_blk_size.to_bytes(4, "little"),
    ])

    print("Writing to file...")
    out_file = Path(tar_file.parent, f"{tar_file.name}.enc")
    with open(out_file, "wb") as of:
        of.write(head)
        of.write(cont)
    print(f"Successfully encrypted file to [{out_file}].")
    print(f"Time: {time.time() - st:.2f}s")


def decrypt_file():
    repo_path = Path(BASE_PATH, REPO_FILENAME)
    with open(repo_path, "r", encoding="utf8") as rf:
        repo = json.load(rf)  # type: dict
    private_keys = repo.get("private", [])
    ln_private_keys = len(private_keys)
    if ln_private_keys == 0:
        print("\nThere is no private keys stored.")
        return None

    print(f"\nThe stored private keys:")
    for i in range(ln_private_keys):
        print(f"{i:>{len(str(ln_private_keys))}}. [{private_keys[i]}]")

    opt, state = request_input(
        "\nChoose the private key you want to use to decrypt",
        "No such option.",
        check_func=lambda x: x.isdigit() and int(x) in range(ln_private_keys),
    )
    if state is False:
        return None

    pvk_f = private_keys[int(opt)]
    n, d = _read_keyfile(pvk_f)
    if n == -1 or d == -1:
        print("Not a valid key file.")
        return None

    rsa = PyRSA()
    rsa.set_private_key((n, d))

    tar_file, state = request_input(
        "\nEnter the file path you want to decrypt",
        "Invalid file path.",
        check_func=_is_file,
    )
    if state is False:
        return None
    tar_file = Path(tar_file)

    with open(tar_file, "rb") as tf:
        head = tf.read(4)
        if head != ENCF_HEAD:
            print("Not an encrypted file.")
            return None
        max_byte_size = int.from_bytes(tf.read(4), "little")
        last_blk_size = int.from_bytes(tf.read(4), "little")
        data = tf.read()

    print("\nStart decrypting...")
    st = time.time()

    dec_nums = []
    ln_but_one = len(data) - max_byte_size
    for i in range(0, ln_but_one, max_byte_size):
        dec_num = int.from_bytes(data[i:i + max_byte_size], "little")
        dec_nums.append(rsa.decrypt(dec_num).to_bytes(BLOCK_SIZE, "little"))
    last_blk = int.from_bytes(data[ln_but_one:], "little")
    dec_nums.append(rsa.decrypt(last_blk).to_bytes(last_blk_size, "little"))

    out_filename = str(tar_file.name)
    if out_filename.endswith(".enc"):
        out_filename = out_filename[:-4]
    else:
        out_filename = f"dec_{out_filename}"
    out_file = Path(tar_file.parent, out_filename)
    cont = b"".join(dec_nums)

    print("Writing to file...")
    with open(out_file, "wb") as of:
        of.write(cont)
    print(f"Successfully decrypted file to [{out_file}].")
    print(f"Time: {time.time() - st:.2f}s")


def main():
    cmd = CliHelper(draw_menu_again=True)
    cmd.add_option(title="Generate New Keys", exec_func=gen_new_keys)
    cmd.add_option(title="Load Key", exec_func=load_key)
    cmd.add_option(title="Encrypt File", exec_func=encrypt_file)
    cmd.add_option(title="Decrypt File", exec_func=decrypt_file)
    cmd.add_exit_option()

    cmd.start_loop()


if __name__ == '__main__':
    main()
