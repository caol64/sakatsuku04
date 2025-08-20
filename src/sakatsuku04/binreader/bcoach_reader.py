from ..dtos import BCoachDto
from ..utils import get_resource_path
from ..constants import conv_32_to_100
from ..io import InputBitStream


coachs_count = 0x752
coachs_bytes = 0x44
offset = 0xD2840
target_bytes = 0x68

class BCoach:
    name: str
    born: int
    abilities = [0] * 53

    def to_dto(self) -> BCoachDto:
        return BCoachDto(
            name=self.name,
            born=self.born,
            pos=self.pos,
            age=self.age,
            rank=self.rank,
            tone_type=self.tone_type,
            cooperation_type=self.cooperation_type,
            wave_type=self.wave_type,
            grow_type_phy=self.grow_type_phy,
            grow_type_tec=self.grow_type_tec,
            grow_type_sys=self.grow_type_sys,
            abilities=self.abilities,
            height=self.height,
            style=self.style,
            super_sub=self.super_sub,
            wild_type=self.wild_type,
            weak_type=self.weak_type,
            tired_type=self.tired_type,
            pop=self.pop,
            desire=self.desire,
            pride=self.pride,
            ambition=self.ambition,
            patient=self.patient,
            persistence=self.persistence,
            foot=self.foot,
            debut_year=self.debut_year,
            signing_difficulty=self.signing_difficulty,
        )


def get_coach(id: int) -> BCoach:
    with open(get_resource_path("bpdata.bin"), "rb") as f:
        f.seek(offset + (id - 20000) * coachs_bytes)
        byte_array = f.read(coachs_bytes)
        return unpack_coach(byte_array)


def unpack_coach(byte_array: bytes) -> BCoach:
    bit_stream = InputBitStream(byte_array)
    bcoach = BCoach()
    bcoach.name = bit_stream.unpack_str(0xc).value
    bit_stream.align(1) # c
    bcoach.born = bit_stream.unpack_bits(8).value # d
    a = bit_stream.unpack_bits(4, 1).value # e
    a = bit_stream.unpack_bits(3, 1).value # f
    a = bit_stream.unpack_bits(8, 1).value # 10
    a = bit_stream.unpack_bits(7, 1).value # 11
    a = bit_stream.unpack_bits(9, 2).value * 100 # 12
    a = bit_stream.unpack_bits(4, 1).value # 14
    a = bit_stream.unpack_bits(4, 1).value # 15
    a = bit_stream.unpack_bits(4, 1).value # 16
    a = bit_stream.unpack_bits(4, 1).value # 17
    a = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 18
    a = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 19
    a = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 1a
    a = bit_stream.unpack_bits(1, 1).value # 1b
    a = bit_stream.unpack_bits(0x10, 2).value # 1c
    a = bit_stream.unpack_bits(3, 1).value # 1e
    a = bit_stream.unpack_bits(3, 1).value # 1f
    a = bit_stream.unpack_bits(3, 1).value # 20
    a = bit_stream.unpack_bits(3, 1).value # 21
    a = bit_stream.unpack_bits(2, 1).value # 22
    a = bit_stream.unpack_bits(3, 1).value # 23
    a = bit_stream.unpack_bits(4, 1).value # 24
    a = bit_stream.unpack_bits(8, 1).value # 25
    a = bit_stream.unpack_bits(4, 1).value # 26
    a = bit_stream.unpack_bits(4, 1).value # 27
    a = bit_stream.unpack_bits(3, 1).value # 28
    a = bit_stream.unpack_bits(2, 1).value # 29
    for i in range(0x35):
        bcoach.abilities[i] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 2a - 5e
    a = bit_stream.unpack_bits(8, 1).value # 5f
    a = bit_stream.unpack_bits(8, 1).value # 60
    a = bit_stream.unpack_bits(5, 1).value # 61
    a = bit_stream.unpack_bits(5, 1).value # 62
    a = bit_stream.unpack_bits(5, 1).value # 63
    a = bit_stream.unpack_bits(5, 1).value # 64
    a = bit_stream.unpack_bits(5, 1).value # 65
    a = bit_stream.unpack_bits(5, 1).value # 66
    a = bit_stream.unpack_bits(3, 1).value # 67

    return bcoach


