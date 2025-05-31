import struct

from .utils import get_resource_path

class Blowfish:

    _p_array = struct.unpack('<18I', bytes([
        0xE8, 0x55, 0x18, 0xAB, 0xEF, 0x52, 0xE0, 0x0C, 0x8F, 0xAB, 0xB5, 0x98, 0x6C, 0xC3, 0xC0, 0x2E,
        0x2E, 0x7C, 0x53, 0xD3, 0x1C, 0x8A, 0x16, 0x2F, 0xC9, 0xDE, 0xEB, 0x5D, 0x19, 0x36, 0xA5, 0x04,
        0x30, 0x09, 0x3E, 0x30, 0x46, 0x9B, 0xED, 0x16, 0xEF, 0x23, 0x41, 0xA1, 0xF1, 0xD8, 0x98, 0x44,
        0xDC, 0xD9, 0x15, 0x20, 0x4D, 0xCE, 0x61, 0x91, 0xE6, 0x60, 0xB6, 0x99, 0xD2, 0x09, 0x98, 0x4E,
        0x02, 0xD5, 0xC5, 0x02, 0x55, 0xA6, 0xE7, 0xF0
    ]))
    _s_boxes = None

    @classmethod
    def s_boxes(cls) -> tuple[int]:
        if cls._s_boxes is None:
            with open(get_resource_path("s_boxes.bin"), "rb") as f:
                cls._s_boxes = struct.unpack('<1024I', f.read())
        return cls._s_boxes

    def en(self, param_1: int, param_2: int) -> tuple[int, int]:
        block0 = param_1  # 初始化 block0
        block1 = param_2  # 初始化 block1

        for i in range(0, 18, 2):
            if i == 0:
                block0 ^= Blowfish._p_array[i]
            else:
                block0 ^= (Blowfish._p_array[i] ^
                            Blowfish.s_boxes()[(block1 & 0xff) + 768] +
                            (Blowfish.s_boxes()[((block1 >> 8) & 0xff) + 512] ^
                            Blowfish.s_boxes()[((block1 >> 16) & 0xff) + 256] +
                            Blowfish.s_boxes()[(block1 >> 24) & 0xff]))
            if i == 16:
                block1 ^= Blowfish._p_array[i + 1]
            else:
                block1 ^= (Blowfish._p_array[i + 1] ^
                            Blowfish.s_boxes()[(block0 & 0xff) + 768] +
                            (Blowfish.s_boxes()[((block0 >> 8) & 0xff) + 512] ^
                            Blowfish.s_boxes()[((block0 >> 16) & 0xff) + 256] +
                            Blowfish.s_boxes()[(block0 >> 24) & 0xff]))
        return block0 & 0xffffffff, block1 & 0xffffffff

    def de(self, param_1: int, param_2: int) -> tuple[int, int]:
        block0 = param_1  # 初始化 block0
        block1 = param_2  # 初始化 block1

        for i in range(17, 0, -2):
            if i == 17:
                block0 ^= Blowfish._p_array[i]
            else:
                block0 ^= (Blowfish._p_array[i] ^
                            Blowfish.s_boxes()[(block1 & 0xff) + 768] +
                            (Blowfish.s_boxes()[((block1 >> 8) & 0xff) + 512] ^
                            Blowfish.s_boxes()[((block1 >> 16) & 0xff) + 256] +
                            Blowfish.s_boxes()[(block1 >> 24) & 0xff]))
            if i == 1:
                block1 ^= Blowfish._p_array[i - 1]
            else:
                block1 ^= (Blowfish._p_array[i - 1] ^
                            Blowfish.s_boxes()[(block0 & 0xff) + 768] +
                            (Blowfish.s_boxes()[((block0 >> 8) & 0xff) + 512] ^
                            Blowfish.s_boxes()[((block0 >> 16) & 0xff) + 256] +
                            Blowfish.s_boxes()[(block0 >> 24) & 0xff]))
        return block0 & 0xffffffff, block1 & 0xffffffff
