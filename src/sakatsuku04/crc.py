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
