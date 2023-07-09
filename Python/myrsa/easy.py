# code: utf8
from os import PathLike
from pyrsa import PyRSA
from genp import get_prime


PUBK_HEAD = b"PUBK"
PVTK_HEAD = b"PVTK"
ENCF_HEAD = b"ENCF"
BLOCK_SIZE = 512


def _gen_pq(n: int):
    p = get_prime(n)
    q = get_prime(n)
    return p, q


def _dec2any(num: int, base: int) -> tuple[int]:
    res = []
    while True:
        q, r = divmod(num, base)
        res.append(r)
        if q == 0:
            break
        num = q
    return tuple(res)


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


def gen_new_keys(key_bit: int, pub_key: str | PathLike, pvt_key: str | PathLike):
    pq_len = abs(key_bit) // 2

    yield 1
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

    with open(pub_key, "wb") as f_pbk, open(pvt_key, "wb") as f_pvk:
        f_pbk.write(b"".join(out_pbk))
        f_pvk.write(b"".join(out_pvk))

    yield 2


def encrypt_file(pbk_f: str | PathLike, tar_file: str | PathLike, out_file: str | PathLike):
    n, e = _read_keyfile(pbk_f)
    if n == -1 or e == -1:
        yield 1
        return

    rsa = PyRSA()
    rsa.set_public_key((n, e))

    with open(tar_file, "rb") as tf:
        data = tf.read()

    yield 2

    last_blk_size = 0
    max_byte_size = 0
    enc_nums = []
    ln_data = len(data)
    for i in range(0, ln_data, BLOCK_SIZE):
        blk = data[i:i + BLOCK_SIZE]
        last_blk_size = len(blk)
        enc_num = rsa.encrypt(int.from_bytes(blk, "little"))
        size = len(_dec2any(enc_num, 256))
        enc_nums.append(enc_num)
        if size > max_byte_size:
            max_byte_size = size

        yield 3, i / ln_data * 100

    cont = b"".join(map(lambda x: x.to_bytes(max_byte_size, "little"), enc_nums))
    head = b"".join([
        ENCF_HEAD,
        max_byte_size.to_bytes(4, "little"),
        last_blk_size.to_bytes(4, "little"),
    ])
    yield 3, 100

    yield 4

    with open(out_file, "wb") as of:
        of.write(head)
        of.write(cont)
    yield 5


def decrypt_file(pvk_f: str | PathLike, tar_file: str | PathLike, out_file: str | PathLike):
    n, d = _read_keyfile(pvk_f)
    if n == -1 or d == -1:
        yield 1
        return

    rsa = PyRSA()
    rsa.set_private_key((n, d))

    with open(tar_file, "rb") as tf:
        head = tf.read(4)
        if head != ENCF_HEAD:
            yield 6
            return
        max_byte_size = int.from_bytes(tf.read(4), "little")
        last_blk_size = int.from_bytes(tf.read(4), "little")
        data = tf.read()

    yield 2

    dec_nums = []
    ln_but_one = len(data) - max_byte_size
    for i in range(0, ln_but_one, max_byte_size):
        dec_num = int.from_bytes(data[i:i + max_byte_size], "little")
        dec_nums.append(rsa.decrypt(dec_num).to_bytes(BLOCK_SIZE, "little"))

        yield 3, i / ln_but_one * 100
    last_blk = int.from_bytes(data[ln_but_one:], "little")
    dec_nums.append(rsa.decrypt(last_blk).to_bytes(last_blk_size, "little"))
    yield 3, 100

    yield 4

    with open(out_file, "wb") as of:
        of.write(b"".join(dec_nums))

    yield 5
