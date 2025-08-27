from ..dtos import BPlayerDto
from ..utils import get_resource_path
from ..constants import conv_32_to_100
from ..io import InputBitStream


players_count = 0x2EC8
players_bytes = 0x48

class BPlayer:
    name: str
    born: int
    pos: int
    age: int
    rank: int
    tone_type: int
    cooperation_type: int
    wave_type: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    abilities = [0] * 64
    height: int
    style: int
    super_sub: int
    wild_type: int
    weak_type: int
    tired_type: int
    pop: int
    desire: int
    pride: int
    ambition: int
    patient: int
    persistence: int
    foot: int
    unlock_year: int
    signing_difficulty: int

    def to_dto(self) -> BPlayerDto:
        return BPlayerDto(
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
            unlock_year=self.unlock_year,
            signing_difficulty=self.signing_difficulty,
        )


def get_player(id: int) -> BPlayer:
    with open(get_resource_path("bpdata.bin"), "rb") as f:
        f.seek(id * players_bytes)
        byte_array = f.read(players_bytes)
        return unpack_player(byte_array)


def unpack_player(byte_array: bytes) -> BPlayer:
    bit_stream = InputBitStream(byte_array)
    bplayer = BPlayer()
    bplayer.name = bit_stream.unpack_str(0xc).value
    bit_stream.align(1) # c
    bplayer.born = bit_stream.unpack_bits(8).value # d
    bit_stream.align(1) # e
    bplayer.rank = bit_stream.unpack_bits(4, 1).value # f
    bplayer.pos = bit_stream.unpack_bits(4, 1).value # 10
    bplayer.age = bit_stream.unpack_bits(5, 1).value + 16 # 11
    bplayer.height = bit_stream.unpack_bits(6, 1).value + 0x96 # 12
    bit_stream.align(1) # 13
    base_number = bit_stream.unpack_bits(7, 1).value # 14
    bplayer.foot = bit_stream.unpack_bits(3, 1).value # 15
    bplayer.unlock_year = bit_stream.unpack_bits(4, 2).value # 16
    un = bit_stream.unpack_bits(0x10).value # 18
    bplayer.signing_difficulty = bit_stream.unpack_bits(9, 2).value * 100 # 1a
    enable_flag = bit_stream.unpack_bits(4, 1).value # 1c
    un = bit_stream.unpack_bits(4, 1).value # 1d
    un = bit_stream.unpack_bits(4, 1).value # 1e
    un = bit_stream.unpack_bits(4, 1).value # 1f
    un = bit_stream.unpack_bits(1, 1).value # 20
    un = bit_stream.unpack_bits(2, 1).value # 21
    un = bit_stream.unpack_bits(4, 1).value # 22
    un = bit_stream.unpack_bits(4, 1).value # 23
    un = bit_stream.unpack_bits(4, 1).value # 24
    un = bit_stream.unpack_bits(4, 1).value # 25
    bplayer.desire = bit_stream.unpack_bits(5, 1).value # 26
    bplayer.pride = bit_stream.unpack_bits(5, 1).value # 27
    bplayer.ambition = bit_stream.unpack_bits(5, 1).value # 28
    bplayer.persistence = bit_stream.unpack_bits(5, 1).value # 29
    un = bit_stream.unpack_bits(5, 1).value # 2a
    bplayer.tone_type = bit_stream.unpack_bits(3, 2).value # 2b
    un = bit_stream.unpack_bits(3, 1).value # 2d
    un = bit_stream.unpack_bits(3, 1).value # 2e
    un = bit_stream.unpack_bits(3, 1).value # 2f
    un = bit_stream.unpack_bits(3, 1).value # 30
    un = bit_stream.unpack_bits(3, 1).value # 31
    bplayer.patient = bit_stream.unpack_bits(3, 1).value # 32
    moti_type = bit_stream.unpack_bits(3, 1).value # 33
    bplayer.cooperation_type = bit_stream.unpack_bits(3, 1).value # 34
    bplayer.wave_type = bit_stream.unpack_bits(3, 1).value # 35
    bplayer.grow_type_phy = bit_stream.unpack_bits(4, 1).value # 36
    bplayer.grow_type_tec = bit_stream.unpack_bits(4, 1).value # 37
    bplayer.grow_type_sys = bit_stream.unpack_bits(4, 1).value # 38
    bplayer.super_sub = bit_stream.unpack_bits(5, 1).value # 39
    un = bit_stream.unpack_bits(4, 1).value # 3a
    bplayer.wild_type = bit_stream.unpack_bits(5, 1).value # 3b
    bplayer.weak_type = bit_stream.unpack_bits(3, 1).value # 3c
    bplayer.tired_type = bit_stream.unpack_bits(3, 1).value # 3d
    # print(un)
    bplayer.pop = bit_stream.unpack_bits(5, 1).value # 3e
    bplayer.style = bit_stream.unpack_bits(5, 1).value # 3f
    style_flag = bit_stream.unpack_bits(1, 1).value # 40
    un = bit_stream.unpack_bits(3, 1).value # 41
    un = bit_stream.unpack_bits(4, 2).value # 42
    bplayer.abilities[0] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 44
    bplayer.abilities[1] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[2] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[3] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[4] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[5] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[6] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[7] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[8] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[9] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0xa] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0xb] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0xc] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0xd] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0xe] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0xf] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x10] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x14] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x15] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x16] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x17] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x18] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x19] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x1a] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x1b] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x1c] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x1d] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x1e] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x1f] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x20] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x21] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x22] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x23] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x24] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x25] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x26] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x27] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x28] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x29] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x2a] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x2b] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x2c] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x2d] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x2e] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x2f] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x30] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x31] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x32] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x33] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x34] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x35] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43
    bplayer.abilities[0x36] = (bplayer.abilities[8] * 7 + bplayer.abilities[0x22] * 3) // 10 # 射手 = （射门 * 7 + FW * 3） // 10
    bplayer.abilities[0x37] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43 # 柱式中锋
    bplayer.abilities[0x38] = (bplayer.abilities[9] * 7 + bplayer.abilities[5] * 3) // 10 # 传球者 = （传球 * 7 + 视野 * 3） // 10
    bplayer.abilities[0x39] = (bplayer.abilities[0xb] * 7 + bplayer.abilities[0xc] * 3) // 10 # 盘球者 = （盘球 * 7 + 控球 * 3） // 10
    bplayer.abilities[0x3a] = (bplayer.abilities[0xa] * 7 + bplayer.abilities[0x20] * 3) // 10 # 边锋 = （传中 * 7 + SMF * 3） // 10
    bplayer.abilities[0x3b] = (bplayer.abilities[0xf] * 7 + bplayer.abilities[0x1d] * 3) // 10 # 中卫 = （铲球 * 7 + CDF * 3） // 10
    bplayer.abilities[0x3c] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43 清道夫
    bplayer.abilities[0x3d] = conv_32_to_100[bit_stream.unpack_bits(5, 1).value] # 43 自由人
    bplayer.abilities[0x3e] = (bplayer.abilities[0x13] * 7 + bplayer.abilities[0x1c] * 3) // 10 # 出击型门将 = （出击 * 7 + GK * 3） // 10
    bplayer.abilities[0x3f] = bit_stream.unpack_bits(4, 1).value * 10 # 43 梦幻之星
    if bplayer.pos == 0:
        bplayer.abilities[0x11] = bplayer.abilities[0x0e]  # 头球 -> 扑球
        bplayer.abilities[0x12] = bplayer.abilities[0x0f]  # 铲球 -> 高球处理
        bplayer.abilities[0x13] = bplayer.abilities[0x10]  # 断球 -> 出击
        # 新头球 = (射门 / 2) + (踢球力 * 0.45)
        new_heading = (bplayer.abilities[8] >> 1) + (bplayer.abilities[0x15] * 0.45)
        # 新铲球 = (攻击意欲 * 0.3) + (爆发力 * 0.35)
        new_tackle = (bplayer.abilities[6] * 0.3) + (bplayer.abilities[0x17] * 0.35)
        # 新断球 = (速度 / 5) + (防守意欲 * 0.28)
        new_passcut = (bplayer.abilities[0x16] // 5) + (bplayer.abilities[7] * 0.28)
        bplayer.abilities[0x0e] = int(new_heading) # 头球
        bplayer.abilities[0x0f] = int(new_tackle) # 铲球
        bplayer.abilities[0x10] = int(new_passcut) # 断球
    else:
        # 扑球 = 身体成长类型 + (爆发力 / 5)
        bplayer.abilities[0x11] = bplayer.grow_type_phy + (bplayer.abilities[0x17] // 5)
        # 高球处理 = 身高 / 10 + 口调 * 2
        bplayer.abilities[0x12] = (bplayer.height // 10) + (bplayer.tone_type * 2)
        # 出击 = 技术成长类型 + (速度 / 5)
        bplayer.abilities[0x13] = bplayer.grow_type_tec + (bplayer.abilities[0x16] // 5)
    return bplayer


