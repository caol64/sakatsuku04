from ..dtos import BScoutDto
from ..utils import get_resource_path
from ..io import InputBitStream


scouts_count = 0x38d
scouts_bytes = 0x2b
offset = 0xF1A08
target_bytes = 0x34

class BScout:
    name: str
    born: int
    abilities = [0] * 21
    area1: int
    area2: int

    def to_dto(self) -> BScoutDto:
        return BScoutDto(
            name=self.name,
            born=self.born,
            abilities=self.abilities,
        )


def get_scout(id: int) -> BScout:
    with open(get_resource_path("bpdata.bin"), "rb") as f:
        f.seek(offset + (id - 30000) * scouts_bytes)
        byte_array = f.read(scouts_bytes)
        return unpack_coach(byte_array)


def unpack_coach(byte_array: bytes) -> BScout:
    bit_stream = InputBitStream(byte_array)
    bscout = BScout()
    bscout.name = bit_stream.unpack_str(0xc).value
    bit_stream.align(1) # c
    bscout.born = bit_stream.unpack_bits(8).value # d
    a = bit_stream.unpack_bits(8, 1).value # e
    rank = bit_stream.unpack_bits(4, 1).value # f
    a = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 10
    a = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 11
    a = bit_stream.unpack_bits(0x10, 2).value # 12
    a = bit_stream.unpack_bits(8, 2).value # 14
    a = bit_stream.unpack_bits(9, 2).value * 100 # 16
    a = bit_stream.unpack_bits(4, 1).value # 18
    a = bit_stream.unpack_bits(4, 1).value # 19
    a = bit_stream.unpack_bits(4, 1).value # 1a
    a = bit_stream.unpack_bits(4, 1).value # 1b
    bscout.abilities[0] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 1c
    bscout.abilities[1] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 1d
    bscout.abilities[2] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 1e
    bscout.abilities[3] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 1f
    bscout.abilities[4] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 20
    bscout.abilities[5] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 21
    bscout.abilities[6] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 22
    bscout.abilities[7] = bit_stream.unpack_bits(6, 1).value * 100 // 63 # 23
    bscout.abilities[8] = bit_stream.unpack_bits(7, 1).value # 24
    bscout.abilities[9] = bit_stream.unpack_bits(7, 1).value # 25
    bscout.abilities[10] = bit_stream.unpack_bits(7, 1).value # 26
    bscout.abilities[11] = bit_stream.unpack_bits(7, 1).value # 27
    bscout.abilities[12] = bit_stream.unpack_bits(7, 1).value # 28
    bscout.abilities[13] = bit_stream.unpack_bits(7, 1).value # 29
    bscout.abilities[14] = bit_stream.unpack_bits(7, 1).value # 2a
    bscout.abilities[15] = bit_stream.unpack_bits(7, 1).value # 2b
    bscout.abilities[16] = bit_stream.unpack_bits(7, 1).value # 2c
    bscout.abilities[17] = bit_stream.unpack_bits(7, 1).value # 2d
    bscout.abilities[18] = bit_stream.unpack_bits(7, 1).value # 2e
    bscout.abilities[19] = bit_stream.unpack_bits(7, 1).value # 2f
    bscout.abilities[20] = bit_stream.unpack_bits(7, 1).value # 30
    bscout.area1 = bit_stream.unpack_bits(8, 1).value # 31
    bscout.area2 = bit_stream.unpack_bits(8, 1).value # 32
    a = bit_stream.unpack_bits(8, 1).value # 33
    return bscout


