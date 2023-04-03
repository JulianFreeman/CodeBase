# coding: utf8
import math


class PyRSA(object):

    def __init__(self, p=1, q=1, e=1):
        self._p = p
        self._q = q
        self._e = e
        self._n = p * q
        self._fn = (p - 1) * (q - 1)
        self._d = 0

    def set_pq(self, p: int, q: int):
        self._p = p
        self._q = q
        self._n = p * q
        self._fn = (p - 1) * (q - 1)

    def set_n(self, n: int):
        self._n = n

    def set_d(self, d: int):
        self._d = d

    def set_valid_e(self, e=0, edge=100) -> int:
        if self._fn == 0:
            raise ValueError("Set valid p and q first")
        if e != 0:
            if math.gcd(e, self._fn) != 1:
                raise ValueError("e and fn have to be coprime")
            else:
                self._e = e
                return e
        # check if the current e is valid
        if self._e != 1:
            if math.gcd(self._e, self._fn) == 1:
                return self._e
        # current e is not valid, so below begin calculating
        if edge > self._fn:
            raise ValueError("The largest possible e cannot be larger than fn")
        pre_es = [30001, 65536, 19, ]

        def calc_e(nums):
            for ie in nums:
                if math.gcd(ie, self._fn) == 1:
                    self._e = ie
                    return ie

        pe = calc_e(pre_es)
        if pe is None:
            pe = calc_e(range(2, edge))
        if pe is None:
            raise ValueError("No valid e was found, try increase edge or set manually")
        # pe is not None
        self._e = pe
        return pe

    def calc_d(self, offset=0):
        if self._fn == 0 or self._e == 1:
            raise ValueError("Set valid p, q and e first")
        if math.gcd(self._e, self._fn) != 1:
            raise ValueError("e and fn have to be coprime")
        for k in range(1, self._e):
            d, r = divmod((1 + k * self._fn), self._e)
            if r == 0:
                d += offset * self._fn
                self._d = d
                return d
        raise ValueError("No valid d was found, try another e ")

    def get_public_key(self) -> tuple[int, int]:
        return self._n, self._e

    def get_private_key(self) -> tuple[int, int]:
        return self._n, self._d

    def set_public_key(self, pub: tuple[int, int]):
        self._n, self._e = pub

    def set_private_key(self, pvt: tuple[int, int]):
        self._n, self._d = pvt

    @staticmethod
    def _fill_0(num: int, step: int) -> str:
        q, r = divmod(len(str(num)), step)
        fz = (q if r == 0 else q + 1) * step
        return f"{num:0{fz}}"

    def encrypt(self, org: int) -> int:
        cph_parts = []
        step = len(str(self._n)) - 1
        f_org = self._fill_0(org, step)
        for np in range(0, len(f_org), step):
            num = int(f_org[np:np + step])
            cph_parts.append(self._fill_0(pow(num, self._e, self._n), step + 1))
        return int("".join(cph_parts))

    def decrypt(self, cph: int) -> int:
        org_parts = []
        step = len(str(self._n))
        f_cph = self._fill_0(cph, step)
        for np in range(0, len(f_cph), step):
            num = int(f_cph[np:np + step])
            org_parts.append(self._fill_0(pow(num, self._d, self._n), step - 1))
        return int("".join(org_parts))


def demo():
    # generate new keys
    rsa1 = PyRSA(p=353, q=307)
    rsa1.set_valid_e()
    rsa1.calc_d()
    pub_k = rsa1.get_public_key()
    pvt_k = rsa1.get_private_key()

    # encrypt
    rsa2 = PyRSA()
    rsa2.set_public_key(pub_k)
    m = 20200725
    c = rsa2.encrypt(m)
    print("origin:", m)
    print("cipher:", c)

    # decrypt
    rsa3 = PyRSA()
    rsa3.set_private_key(pvt_k)
    n = rsa3.decrypt(c)
    print("origin:", n)
