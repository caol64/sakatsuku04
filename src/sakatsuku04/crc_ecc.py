import struct

from .utils import get_resource_path


class CrcCaculator:

    _mask1 = 0x9255AE41
    _mask2 = 0xEFCFBFEA
    _crc_table = None

    @classmethod
    def crc_table(cls) -> tuple[int]:
        if cls._crc_table is None:
            with open(get_resource_path("crc_table.bin"), "rb") as f:
                cls._crc_table = struct.unpack('<256H', f.read())
        return cls._crc_table

    def calc(self, data: bytes) -> tuple[int, int]:
        crc = 0xFFFF
        for byte in data:
            crc = (crc >> 8) ^ CrcCaculator.crc_table()[(crc & 0xFF) ^ byte]
        crc ^= 0xFFFF
        left = crc & CrcCaculator._mask1 | CrcCaculator._mask2 & ~CrcCaculator._mask1
        right = crc & ~CrcCaculator._mask1 | CrcCaculator._mask2 & CrcCaculator._mask1
        return (left, right)


def _parityb(a):
    a = (a ^ (a >> 1))
    a = (a ^ (a >> 2))
    a = (a ^ (a >> 4))
    return a & 1


def _make_ecc_tables():
    parity_table = [_parityb(b) for b in range(256)]
    cpmasks = [0x55, 0x33, 0x0F, 0x00, 0xAA, 0xCC, 0xF0]

    column_parity_masks = [None] * 256
    for b in range(256):
        mask = 0
        for i in range(len(cpmasks)):
            mask |= parity_table[b & cpmasks[i]] << i
            column_parity_masks[b] = mask

    return parity_table, column_parity_masks


_parity_table, _column_parity_masks = _make_ecc_tables()


class EccCaculator:
    """Calculate the Hamming code for a 128 byte long byte array."""

    def calc(self, data: bytes) -> bytes:
        column_parity = 0x77
        line_parity_0 = 0x7F
        line_parity_1 = 0x7F
        for i in range(len(data)):
            b = data[i]
            column_parity ^= _column_parity_masks[b]
            if _parity_table[b]:
                line_parity_0 ^= ~i
                line_parity_1 ^= i
        return bytes([column_parity, line_parity_0 & 0x7F, line_parity_1])
