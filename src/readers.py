from bit_stream import BitStream, InputBitStream
from const import Const
from models import Club, MyPlayer, MyTeam, OtherTeam, Player, PlayerAbility
from utils import decode_bytes_to_str

class BaseReader:
    def __init__(self, bit_stream: InputBitStream):
        self.bit_stream = bit_stream

class RandomReader(BaseReader):
    start_offset = 0x703D50
    money_address = (26, 0x20)
    def read(self):
        bit_offset, bit_length = RandomReader.money_address
        self.bit_stream.seek(bit_offset)
        money = self.bit_stream.read_bits(bit_length)
        print(money)

    def write(self, money: int):
        bit_offset, bit_length = RandomReader.money_address
        byte_index = bit_offset // 8
        bit_index = bit_offset % 8
        current_byte = self.bit_stream.input_data[byte_index]
        print(byte_index, bit_index, current_byte)

class ClubReader(BaseReader):
    start_bytes = 0
    block_bytes = 5044
    total_bytes = 5044
    start_offset = 0x703D50
    consume_bytes = 0x127D
    consume_bits = 0x93E5
    remain_mask = 0x4

    def read(self) -> Club:
        club = Club()
        club.year, club.month, club.date, club.day = self.bit_stream.unpack_bits([0xE, 4, 5, 3], 8)
        club.money, = self.bit_stream.unpack_bits([0x20])
        club.club_info = self.bit_stream.unpack_bits([8] * 0x200) # 00703D5C - 00703F5C
        self.bit_stream.skip(ClubReader.consume_bits, ClubReader.total_bytes - sum(self.bit_stream.total_bytes_list))
        return club
        # self.club.club_info = self.bit_stream.bit_read_str(0x200) # 00703D5C - 00703F5C

        # self.bit_stream.alloc(ClubReader.total_bytes - len(self.bit_stream.out_buffer))
        # self.bit_stream.skip(ClubReader.consume_bytes, ClubReader.remain_mask)
        # elements = [
        #     3, -0x10, -0x10, -0x20, 0xb, 1, 1, 1, 8, 8, 8, 8, (0xb, 0x222), 0xb, 0xb, 0xb, 0xb, 0xb, 0xb, 0xb,
        #     8, 8, 8, 8, 8, 8, 8, 8, 8, (4, 0x23c)
        # ]
        # self.bit_stream.batch_read(elements)
        # self.bit_stream.align(32)
        # for i in range(0x20):
        #     self.bit_stream.bit_read(0x20)

        # for i in range(0x32):
        #     # self.bit_stream.align(32)
        #     # self.bit_stream.bit_read(0x10)
        #     # self.bit_stream.bit_read(8)
        #     # self.bit_stream.bit_read(8)
        #     # self.bit_stream.bit_read(8)
        #     # for j in range(0x10):
        #     #     self.bit_stream.bit_read(0x20)
        #     self.bit_stream.bit_read(0x10, i * 0x24 + 0x2c0)
        #     self.bit_stream.bit_read(8, i * 0x24 + 0x2c2)
        #     if i % 2 == 0:
        #         self.bit_stream.bit_read(8, i * 0x48 + 0x2c3)
        #     self.bit_stream.bit_read(8, i * 0x24 + 0x2c4)
        #     for j in range(0x10):
        #         self.bit_stream.bit_read(0x20, i * 0x24 + j * 4 + 0x2c8)
        # # self.bit_stream.align(32)
        # for i in range(0x30):
        #     # self.bit_stream.bit_read(0x20)
        #     self.bit_stream.bit_read(0x20, i * 2 + 0x868)
        # for i in range(0x20):
        #     # self.bit_stream.bit_read(0x10)
        #     # self.bit_stream.bit_read(8)
        #     self.bit_stream.bit_read(0x10, i * 2 + 0x8c8)
        #     self.bit_stream.bit_read(8, i * 2 + 0x8c9)
        # for i in range(0x20):
        #     # self.bit_stream.bit_read(0x10)
        #     # self.bit_stream.bit_read(8)
        #     self.bit_stream.bit_read(0x10, i * 2 + 0x908)
        #     self.bit_stream.bit_read(8, i * 2 + 0x909)
        # for i in range(0x20):
        #     # self.bit_stream.bit_read(0x10)
        #     # self.bit_stream.bit_read(8)
        #     self.bit_stream.bit_read(0x10, i * 2 + 0x948)
        #     self.bit_stream.bit_read(8, i * 2 + 0x949)
        # for i in range(0x20):
        #     # self.bit_stream.bit_read(0x10)
        #     # self.bit_stream.bit_read(8)
        #     self.bit_stream.bit_read(0x10, i * 2 + 0x988)
        #     self.bit_stream.bit_read(8, i * 2 + 0x989)
        # self.bit_stream.bit_read(0x10, 0x9ac)
        # for i in range(2):
        #     self.bit_stream.bit_read(8, i * 4 + 0x9ad)
        #     self.bit_stream.bit_read(8, i * 8 + 0x135b)
        #     self.bit_stream.bit_read(8, i * 4 + 0x9ae)
        #     self.bit_stream.bit_read(8, i * 8 + 0x135d)
        #     self.bit_stream.bit_read(8, i * 4 + 0x9af)
        #     self.bit_stream.bit_read(8, i * 8 + 0x135f)
        #     self.bit_stream.bit_read(0x10, i * 4 + 0x9b0)
        # self.bit_stream.bit_read(8, 0x9b5)
        # self.bit_stream.bit_read(8, 0x136b)
        # self.bit_stream.bit_read(0x10, 0x9b6)
        # self.bit_stream.bit_read(0x10, 0x9b7)
        # for i in range(5):
        #     self.bit_stream.bit_read(0x10, i + 0x9b8)
        # self.bit_stream.bit_read(0x20, 0x9be)
        # self.bit_stream.bit_read(0x20, 0x9c0)
        # self.bit_stream.bit_read(8, 0x9c2)
        # self.bit_stream.bit_read(5, 0x1385)
        # self.bit_stream.bit_read(0x10, 0x9c3)
        # self.bit_stream.bit_read(1, 0x9c4)
        # self.bit_stream.bit_read(0x20, 0x9c6)
        # for i in range(2):
        #     self.bit_stream.bit_read(0x20, i * 2 + 0x9c8)
        # self.bit_stream.bit_read(8, 0x9cc)
        # self.bit_stream.bit_read(8, 0x1399)
        # self.bit_stream.bit_read(0x20, 0x9ce)
        # for i in range(3):
        #     self.bit_stream.bit_read(8, i)


class TeamReader(BaseReader):
    start_bytes = 0x13B4
    block_bytes = 161516
    total_bytes = 166560
    start_offset = 0x705104
    consume_bytes = 0x1836C
    consume_bits = 0xC1B5C
    remain_mask = 0x8

    def read(self) -> MyTeam:
        team = MyTeam()
        self.bit_stream.unpack_bits([8, 1, 1], 4)
        self.bit_stream.unpack_bits([16])
        self.bit_stream.unpack_bits([8] * 40)
        team.english_name = self.bit_stream.unpack_bits([8] * 0x20)
        self.bit_stream.unpack_bits([8] * 57)
        team.oilis_english_name = self.bit_stream.unpack_bits([8] * 0x20)
        self.bit_stream.unpack_bits([8] * 15)
        self.bit_stream.unpack_bits([16, 16, 8, 8]) # 7051BF
        team.players = self.read_players()
        self.read_players()

        # 643 0070DD78

        self.bit_stream.skip(TeamReader.consume_bits, TeamReader.total_bytes - sum(self.bit_stream.total_bytes_list))
        return team

    def read_players(self) -> list[MyPlayer]:
        players: list[MyPlayer] = [MyPlayer() for _ in range(0x19)]
        self.bit_stream.unpack_bits([16, 16, 1], 5)
        self.bit_stream.unpack_bits([-6] * 0x19, 0x19 + 2) # 7051E0
        for i in range(0x19): #0x19
            players[i].id, _, players[i].age = self.bit_stream.unpack_bits([-0x10, 4, 7], 4) # 7051E4
            players[i].name = Const.PLAYER_DICT.get(f"{players[i].id:04X}")
            for l in range(0x40):
                current, current_max, max = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
                players[i].abilities.append(PlayerAbility(Const.ABILITY_LIST[l], current, current_max, max)) # 705364
            self.bit_stream.unpack_bits([0xb], 2)
            players[i].saved_name = self.bit_stream.unpack_bits([8] * 0xd) # 705373
            self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7], 11) # 70537E
            self.bit_stream.unpack_bits([0x10, 0x10])# 705382
            self.bit_stream.unpack_bits([4, 4, 4, 4, 1, 2, 4, 4, 4, 4, 7, 7, 7, 7, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4], 28) # 70539E
            self.bit_stream.unpack_bits([4, 7, 4, 7, 3, 3, 7, 5, 1, 3, 4], 14) # 7053AC
            self.bit_stream.unpack_bits([0x20, 2], 6)
            self.bit_stream.unpack_bits([0xa, 8, 8, 0x10], 6) # 7053B8
            self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 8], 6)
            self.bit_stream.unpack_bits([0x10] * 14, 30) # 7053DC
            self.bit_stream.unpack_bits([0x20, -0x10, 0x10, 0x10, 0x10, 0x10], 14)
            self.bit_stream.unpack_bits([4, 7, 4, 7, 6, 4, 8, 4, 0x10, 0x10, 7], 13)
            self.bit_stream.unpack_bits([-8] * 9, 9)
            self.bit_stream.unpack_bits([0x10, 0x10, 8, -8, 5, 5, 6], 12)
            self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 0x20, 0x10], 20) # 705420
        self.bit_stream.unpack_bits([0x10])
        for _ in range(10):
            self.bit_stream.unpack_bits([-6], 2)
            self.bit_stream.unpack_bits([0x10]) # 708A4A
        self.bit_stream.unpack_bits([-6, -6, 5, -6, -6, -6, -6, -6, 2], 9)
        self.bit_stream.unpack_bits([5, 3, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3] * 3, 60)
        self.bit_stream.align(1)
        self.bit_stream.unpack_bits([0x10] * (0x19 * 0x19)) # 708F72
        self.bit_stream.unpack_bits([8] * 3)
        self.bit_stream.unpack_bits([8] * 0x19)
        self.bit_stream.unpack_bits([3], 2)
        coach_name = self.bit_stream.unpack_bits([8] * 0xd) # coach name
        self.bit_stream.unpack_bits([8, 4, 3, 8, 7, 0x10, 4, 4, 4, 4, 7, 7, 7, 1, -0x10, 3, 3, 3, 3, 2, 3, 4, 8, 4, 4, 3, 2], 29) # 708FBA
        self.bit_stream.unpack_bits([7] * 0x35, 0x35)
        self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 15)
        self.bit_stream.unpack_bits([0x10] * 9)
        self.bit_stream.unpack_bits([1], 2)
        self.bit_stream.unpack_bits([3, 1], 2)
        for _ in range(0xc):
            self.bit_stream.unpack_bits([8, 8, 1, 1], 4)
            self.bit_stream.unpack_bits([1] * 0x19, 0x19)
            self.bit_stream.unpack_bits([8, 5, 5, 8, 3] * 12, 5 * 12)
        self.bit_stream.unpack_bits([8, 3] * (0x19 * 0xc), 2 * (0x19 * 0xc))
        for _ in range(7):
            self.bit_stream.unpack_bits([8])
            for _ in range(3):
                self.bit_stream.unpack_bits([-6, 8], 2)
                self.bit_stream.unpack_bits([8] * 0xa)
        self.bit_stream.unpack_bits([8])
        return players


class OtherTeamReader(BaseReader):
    start_bytes = 0x28AA0
    block_bytes = 35264
    total_bytes = 201824
    start_offset = 0x72C7F0
    consume_bytes = 0x208B5
    remain_mask = 0x20


    def read(self) -> list[OtherTeam]:
        teams: list[OtherTeam] = list()
        for i in range(0x109): # loop the teams
            other_team = OtherTeam()
            other_team.id, = self.bit_stream.unpack_bits([0x10])
            players: list[Player] = list()
            for _ in range(0x19): # loop the playes
                player = Player()
                player.id, player.age, player.ability_graph = self.bit_stream.unpack_bits([0x10, 7, 8], 4)
                player.update_name_from_dict()
                players.append(player)
            other_team.unknown1, other_team.friendly, other_team.unknown2 = self.bit_stream.unpack_bits([0x10, 0x10, 7], 6) # 72c85b
            other_team.name = Const.TEAM_LIST[i]
            other_team.players = players
            teams.append(other_team)
        for i in range(0x109):
            for j in range(0x19):
                teams[i].players[j].no, = self.bit_stream.unpack_bits([8]) # 背番号
        self.bit_stream.unpack_bits([8, 8])
        return teams


class LeagueReader(BaseReader):
    start_bytes = 0x31460
    block_bytes = 832
    total_bytes = 202656
    start_offset = 0x7351B0
    consume_bytes = 0x20AEA
    remain_mask = 0x80

    def __init__(self, bit_stream: BitStream):
        self.bit_stream = bit_stream

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)

class TownReader(BaseReader):
    start_bytes = 0x317A0
    block_bytes = 380
    total_bytes = 203036
    start_offset = 0x7354F0
    consume_bytes = 0x20B72
    remain_mask = 0x4

    def __init__(self, bit_stream: BitStream):
        super().__init__(bit_stream)

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)

class RecordReader(BaseReader):
    start_bytes = 0x33191C
    block_bytes = 189200
    total_bytes = 392236
    start_offset = 0x73566C
    consume_bytes = 0x41B1F
    remain_mask = 0x2

    def __init__(self, bit_stream: BitStream):
        super().__init__(bit_stream)

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)

class ScheReader(BaseReader):
    start_bytes = 0x5FC2C
    block_bytes = 2580
    total_bytes = 394816
    start_offset = 0x76397C
    consume_bytes = 0x4221F
    remain_mask = 0x2

    def __init__(self, bit_stream: BitStream):
        super().__init__(bit_stream)

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)

class OptionReader(BaseReader):
    start_bytes = 0x60640
    block_bytes = 56
    total_bytes = 394872
    start_offset = 0x764390
    consume_bytes = 0x42237
    remain_mask = 0x40

    def __init__(self, bit_stream: BitStream):
        super().__init__(bit_stream)

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)

class MailReader(BaseReader):
    start_bytes = 0x60678
    block_bytes = 0
    total_bytes = 0
    start_offset = 0x7643C8
    consume_bytes = 0
    remain_mask = 0

    def __init__(self, bit_stream: BitStream):
        super().__init__(bit_stream)

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)