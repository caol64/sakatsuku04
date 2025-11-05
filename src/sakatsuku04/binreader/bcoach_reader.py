from ..constants import conv_32_to_100
from ..dtos import BCoachDto
from ..io import InputBitStream
from ..utils import get_resource_path

coachs_count = 0x752
coachs_bytes = 0x44
offset = 0xD2840
target_bytes = 0x68


class BCoach:
    name: str
    born: int
    age: int
    rank: int
    abilities = [0] * 53
    salary: int
    signing_difficulty: int
    styles = [0] * 6
    coach_type: int
    x11: int
    x14: int
    x15: int
    x16: int
    x17: int
    desire: int
    ambition: int
    persistence: int
    tone_type: int
    salary: int
    t1: int
    t2: int
    t3: int
    t4: int
    x22: int
    cooperation_type: int
    ambition2: int
    manager_style: int
    activate_plan: int
    custom_style: int
    training_plan: int
    training_strength: int
    ac_sp_practice1: int
    ac_sp_practice2: int
    philosophy_id: int

    def to_dto(self) -> BCoachDto:
        return BCoachDto(
            name=self.name,
            born=self.born,
            abilities=self.abilities,
            age=self.age,
            rank=self.rank,
            salary_high=self.salary * 100 // 10000,
            salary_low=self.salary * 100 % 10000,
            signing_difficulty=self.signing_difficulty,
            styles=self.styles,
            coach_type=self.coach_type,
            desire=self.desire,
            ambition=self.ambition,
            persistence=self.persistence,
            activate_plan=self.activate_plan,
            training_plan=self.training_plan,
            training_strength=self.training_strength,
            ac_sp_practice1=self.ac_sp_practice1,
            ac_sp_practice2=self.ac_sp_practice2,
        )


def get_coach(id: int) -> BCoach:
    with open(get_resource_path("bpdata.bin"), "rb") as f:
        f.seek(offset + (id - 20000) * coachs_bytes)
        byte_array = f.read(coachs_bytes)
        return unpack_coach(byte_array)


def unpack_coach(byte_array: bytes) -> BCoach:
    bit_stream = InputBitStream(byte_array)
    bcoach = BCoach()
    bcoach.name = bit_stream.unpack_str(0xC).value
    bit_stream.align(1)  # c
    bcoach.born = bit_stream.unpack_bits(8).value  # d
    bcoach.rank = bit_stream.unpack_bits(4, 1).value  # e
    bcoach.coach_type = bit_stream.unpack_bits(3, 1).value  # f
    bcoach.age = bit_stream.unpack_bits(8, 1).value  # 10
    bcoach.x11 = bit_stream.unpack_bits(7, 1).value  # 11
    bcoach.signing_difficulty = bit_stream.unpack_bits(9, 2).value * 100  # 12
    bcoach.x14 = bit_stream.unpack_bits(4, 1).value  # 14
    bcoach.x15 = bit_stream.unpack_bits(4, 1).value  # 15
    bcoach.x16 = bit_stream.unpack_bits(4, 1).value  # 16
    bcoach.x17 = bit_stream.unpack_bits(4, 1).value  # 17
    bcoach.desire = conv_32_to_100[bit_stream.unpack_bits(5, 1).value]  # 18
    bcoach.ambition = conv_32_to_100[bit_stream.unpack_bits(5, 1).value]  # 19
    bcoach.persistence = conv_32_to_100[bit_stream.unpack_bits(5, 1).value]  # 1a
    bcoach.tone_type = bit_stream.unpack_bits(1, 1).value  # 1b
    bcoach.salary = bit_stream.unpack_bits(0x10, 2).value  # 1c
    bcoach.t1 = bit_stream.unpack_bits(3, 1).value  # 1e
    bcoach.t2 = bit_stream.unpack_bits(3, 1).value  # 1f
    bcoach.t3 = bit_stream.unpack_bits(3, 1).value  # 20
    bcoach.t4 = bit_stream.unpack_bits(3, 1).value  # 21
    bcoach.x22 = bit_stream.unpack_bits(2, 1).value  # 22
    bcoach.cooperation_type = bit_stream.unpack_bits(3, 1).value  # 23
    bcoach.ambition2 = bit_stream.unpack_bits(4, 1).value  # 24
    bcoach.manager_style = bit_stream.unpack_bits(8, 1).value  # 25
    bcoach.activate_plan = bit_stream.unpack_bits(4, 1).value  # 26
    bcoach.custom_style = bit_stream.unpack_bits(4, 1).value  # 27
    bcoach.training_plan = bit_stream.unpack_bits(3, 1).value  # 28
    bcoach.training_strength = bit_stream.unpack_bits(2, 1).value  # 29
    for i in range(0x35):
        bcoach.abilities[i] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value]  # 2a - 5e
    bcoach.ac_sp_practice1 = bit_stream.unpack_bits(8, 1).value  # 5f
    bcoach.ac_sp_practice2 = bit_stream.unpack_bits(8, 1).value  # 60
    for i in range(6):
        bcoach.styles[i] = bit_stream.unpack_bits(5, 1).value  # 61 - 66
    bcoach.philosophy_id = bit_stream.unpack_bits(3, 1).value  # 67
    return bcoach
