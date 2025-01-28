from bit_stream import InputBitStream
from models import Club, MyPlayer, MyTeam, OtherTeam, OtherPlayer, PlayerAbility

class BaseReader:
    base_offset = 0x703D50

    def __init__(self, bit_stream: InputBitStream):
        self.bit_stream = bit_stream

    def print_mem_offset(self):
        print(hex(self.bit_stream.unpacked_bytes_length + ClubReader.start + BaseReader.base_offset))

class ClubReader(BaseReader):
    start = 0 # 0x703D50
    size = 0x13B4
    total_size = size
    consume_bytes = 0x127D
    consume_bits = 0x93E5
    remain_mask = 0x4
    tail_padding = b'\xec\x76\x13\x89' * 4

    def read(self) -> Club:
        club = Club()
        club.year, club.month, club.date, club.day = self.bit_stream.unpack_bits([0xE, 4, 5, 3], 8)
        club.funds = self.bit_stream.unpack_bits(0x20)
        club.manager_name = self.bit_stream.unpack_str(0x10) # 00703D5C
        self.bit_stream.unpack_str(0x10)
        club.club_name = self.bit_stream.unpack_str(0x15)
        self.bit_stream.unpack_str(0x1CB) #  - 00703F5B
        self.bit_stream.unpack_bits(3, 2)
        self.bit_stream.unpack_bits([0x10, 0x10], 6)
        self.bit_stream.unpack_bits([0x20, 0xb, 1, 1, 1, 8, 8, 8, 8, 0xb, 0xb, 0xb, 0xb, 0xb, 0xb, 0xb, 0xb], 30) # 0x703f82
        self.bit_stream.unpack_bits([8, 8, 8, 8, 8, 8, 8, 8, 8, 4], 14) # 0x703f90
        self.bit_stream.unpack_bits([0x20] * 0x20) # 0x704010
        for i in range(0x32):
            self.bit_stream.unpack_bits([0x10, 8, 8, 8], 8)
            self.bit_stream.unpack_bits([0x20] * 0x10)
        self.bit_stream.unpack_bits([0x20] * 0x30)
        for i in range(0x72):
            self.bit_stream.unpack_bits([0x10, 8], 4)
        # 0x7050a8
        self.bit_stream.unpack_bits([0x10, 8, 8, 8, 8, 8, 8, 0x10, 8, 8, 8, 8, 8, 8, 0x10, 8, 8, 0x10, 0x10])
        # 0x7050c0
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10, 0x10], 12)
        # 0x7050cc
        seed = self.bit_stream.unpack_bits(0x20) # maybe random seed?
        # 0x7050d0
        self.bit_stream.unpack_bits([0x20, 8, 5, 0x10, 1], 12)
        self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 8, 8], 16)
        self.bit_stream.unpack_bits([0x20, 8, 8, 8], 8)
        # 0x7050f4
        self.bit_stream.padding(self.tail_padding)
        # 0x705104
        return club


class TeamReader(BaseReader):
    start = ClubReader.start + ClubReader.size # 0x705104
    size = 0x276EC
    total_size = ClubReader.total_size + size
    consume_bytes = 0x1836C
    consume_bits = 0xC1B5C
    remain_mask = 0x8
    tail_padding = b'\xc0\x89\x3f\x76' * 4

    def read(self) -> MyTeam:
        team = MyTeam()
        self.bit_stream.unpack_bits([8, 1, 1], 4)
        self.bit_stream.unpack_bits(16)
        self.bit_stream.unpack_bits([8] * 40)
        team.english_name = self.bit_stream.unpack_str(0x20)
        self.bit_stream.unpack_bits([8] * 57)
        team.oilis_english_name = self.bit_stream.unpack_str(0x20)
        self.bit_stream.unpack_bits([8] * 15)
        self.bit_stream.unpack_bits([16, 16, 8, 8]) # 7051BF
        team.players = self.read_players()
        self.read_players()
        # 0070DD78
        for _ in range(20):
            self.bit_stream.unpack_bits(0x10)
            a = self.bit_stream.unpack_str(0xd)
            self.bit_stream.unpack_bits([8] * 0x15, 0x16)
            self.bit_stream.unpack_bits([8] * 0x2b)
            self.bit_stream.unpack_bits(0x10)
        self.bit_stream.unpack_bits([0x10, 4, 7], 4)
        for _ in range(0x40):
            a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        self.bit_stream.unpack_bits(0xb)
        a = self.bit_stream.unpack_str(0xd)
        self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7, 0x10, 0x10, 4, 4, 4, 4], 18)
        # 0070E584 708
        self.bit_stream.skip(TeamReader.consume_bits, TeamReader.total_size - self.bit_stream.unpacked_bytes_length)
        return team

    def read_players(self) -> list[MyPlayer]:
        # 0x7051c0
        players: list[MyPlayer] = [MyPlayer() for _ in range(0x19)]
        self.bit_stream.unpack_bits([16, 16, 1], 5)
        self.bit_stream.unpack_bits([-6] * 0x19, 0x19 + 2) # 7051E0
        # each player produce 0x240 bytes
        for i in range(0x19): #0x19
            players[i].id, _, players[i].age = self.bit_stream.unpack_bits([-0x10, 4, 7], 4) # 7051E4
            players[i].set_player()
            for l in range(0x40):
                current, current_max, max = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
                players[i].abilities.append(PlayerAbility(l, current, current_max, max)) # 705364
            self.bit_stream.unpack_bits(0xb) # unknown
            players[i].name = self.bit_stream.unpack_str(0xd)
            a = self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7], 11) # 70537E
            players[i].born = a[0] # 705373
            born2 = a[1] # 705374
            players[i].height = a[5] # 705378
            players[i].number = a[7] # 70537A
            players[i].foot = a[8] # 70537B
            a = self.bit_stream.unpack_bits([0x10, 0x10]) # 705382
            a = self.bit_stream.unpack_bits([4, 4, 4, 4, 1, 2, 4, 4, 4, 4, 7, 7, 7, 7, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4], 28) # 70539E
            players[i].grow_type = a[10]
            players[i].tone_type = a[15]
            a = self.bit_stream.unpack_bits([4, 7, 4, 7, 3, 3, 7, 5, 1, 3, 4], 14) # 7053AC
            players[i].skill = a[7]
            a = self.bit_stream.unpack_bits([0x20, 2], 6)
            injured = a[0] # 7053AC
            # print(bin(injured.value))
            a = self.bit_stream.unpack_bits([0xa, 8, 8, 0x10], 6) # 7053B8
            # print([z.value for z in a ])
            a = self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 8], 6)
            a = self.bit_stream.unpack_bits([0x10] * 14, 30) # 7053DC
            a = self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10, 0x10, 0x10, 4, 7, 4, 7, 6, 4, 8, 4], 22)
            players[i].abroad_days = a[5] # 7053E8
            players[i].abroad_times = a[13] # 7053F1
            a = self.bit_stream.unpack_bits([0x10, 0x10, 7])
            a = self.bit_stream.unpack_bits([-8] * 9, 9)
            a = self.bit_stream.unpack_bits([0x10, 0x10, 8, -8, 5, 5, 6], 12)
            a = self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 0x20, 0x10], 20) # 705420
        self.bit_stream.unpack_bits(0x10)
        for _ in range(10):
            self.bit_stream.unpack_bits([-6], 2)
            self.bit_stream.unpack_bits(0x10) # 708A4A
        self.bit_stream.unpack_bits([-6, -6, 5, -6, -6, -6, -6, -6, 2], 9)
        self.bit_stream.unpack_bits([5, 3, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3] * 3, 60)
        self.bit_stream.align(1)
        a = self.bit_stream.unpack_bits([0x10] * (0x19 * 0x19)) # 708F72
        self.bit_stream.unpack_bits([8] * 3)
        a = self.bit_stream.unpack_bits([8] * 0x19)
        self.bit_stream.unpack_bits(3, 2)
        coach_name = self.bit_stream.unpack_str(0xd) # coach name
        a = self.bit_stream.unpack_bits([8, 4, 3, 8, 7, 0x10, 4, 4, 4, 4, 7, 7, 7, 1, -0x10, 3, 3, 3, 3, 2, 3, 4, 8, 4, 4, 3, 2], 29) # 708FBA
        a = self.bit_stream.unpack_bits([7] * 0x35, 0x35)
        # print([z.value for z in a ])
        self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 15)
        self.bit_stream.unpack_bits([0x10] * 9)
        self.bit_stream.unpack_bits(1, 2)
        self.bit_stream.unpack_bits([3, 1], 2)
        for _ in range(0xc):
            self.bit_stream.unpack_bits([8, 8, 1, 1], 4)
            self.bit_stream.unpack_bits([1] * 0x19, 0x19)
            self.bit_stream.unpack_bits([8, 5, 5, 8, 3] * 12, 5 * 12)
        self.bit_stream.unpack_bits([8, 3] * (0x19 * 0xc), 2 * (0x19 * 0xc))
        for _ in range(7):
            self.bit_stream.unpack_bits(8)
            for _ in range(3):
                self.bit_stream.unpack_bits([-6, 8], 2)
                self.bit_stream.unpack_bits([8] * 0xa)
        self.bit_stream.unpack_bits(8)
        return players


class OtherTeamReader(BaseReader):
    start = TeamReader.start + TeamReader.size # 0x72c7f0
    size = 0x89C0
    total_size = TeamReader.total_size + size
    consume_bytes = 0x208B5
    consume_bits = 0x1045A2
    remain_mask = 0x20
    tail_padding = b'\x40\x03\xbf\xfc' * 4


    def read(self) -> list[OtherTeam]:
        teams: list[OtherTeam] = list()
        for i in range(0x109): # loop the teams
            id = self.bit_stream.unpack_bits(0x10)
            players: list[OtherPlayer] = list()
            for _ in range(0x19): # loop the playes
                pid, age, ability_graph = self.bit_stream.unpack_bits([0x10, 7, 8], 4)
                player = OtherPlayer(pid, age, ability_graph)
                players.append(player)
            unknown1, unknown2, friendly = self.bit_stream.unpack_bits([0x10, 0x10, 7], 6) # 72c856 - 72c85b
            other_team = OtherTeam(i, id, friendly, unknown1, unknown2, players)
            teams.append(other_team)
        # 7337bc
        for i in range(0x109):
            for j in range(0x19):
                teams[i].players[j].number = self.bit_stream.unpack_bits(8) # 背番号
        # 73519d
        self.bit_stream.unpack_bits([8, 8], 3)
        # 0x7351a0
        self.bit_stream.padding(self.tail_padding)
        return teams


class LeagueReader(BaseReader):
    start = OtherTeamReader.start + OtherTeamReader.size # 0x7351b0
    size = 0x340
    total_size = OtherTeamReader.total_size + size
    consume_bytes = 0x20AEA
    consume_bits = 0x105750
    remain_mask = 0x80

    def read(self):
        self.bit_stream.unpack_bits(0x20)
        self.bit_stream.skip(LeagueReader.consume_bits, LeagueReader.total_size - self.bit_stream.unpacked_bytes_length)

class TownReader(BaseReader):
    start = LeagueReader.start + LeagueReader.size
    size = 0x17C
    total_size = LeagueReader.total_size + size
    consume_bytes = 0x20B72
    consume_bits = 0x105B8D
    remain_mask = 0x4

    def read(self):
        self.bit_stream.unpack_bits(3, 1)
        self.bit_stream.skip(TownReader.consume_bits, TownReader.total_size - self.bit_stream.unpacked_bytes_length)

class RecordReader(BaseReader):
    start = TownReader.start + TownReader.size
    size = 0x2E310
    total_size = TownReader.total_size + size
    consume_bytes = 0x41B1F
    consume_bits = 0x20D8F6
    remain_mask = 0x2

    def read(self):
        self.bit_stream.unpack_bits(0x10)
        self.bit_stream.skip(RecordReader.consume_bits, RecordReader.total_size - self.bit_stream.unpacked_bytes_length)

class ScheReader(BaseReader):
    start = RecordReader.start + RecordReader.size
    size = 0xA14
    total_size = RecordReader.total_size + size
    consume_bytes = 0x4221F
    consume_bits = 0x2110F8
    remain_mask = 0x2

    def read(self):
        for _ in range(11):
            self.bit_stream.unpack_bits(5)
        self.bit_stream.skip(ScheReader.consume_bits, ScheReader.total_size - self.bit_stream.unpacked_bytes_length)

class OptionReader(BaseReader):
    start = ScheReader.start + ScheReader.size
    size = 0x38
    total_size = ScheReader.total_size + size
    consume_bytes = 0x42237
    consume_bits = 0x2111B8
    remain_mask = 0x40

    def read(self):
        self.bit_stream.unpack_bits(0x20)
        for _ in range(0xd):
            self.bit_stream.unpack_bits(1, 4)
            
        # self.bit_stream.skip(OptionReader.consume_bits, OptionReader.total_size - self.bit_stream.unpacked_bytes_length)

class MailReader(BaseReader):
    start = OptionReader.start + OptionReader.size
    size = 0x1
    total_size = OptionReader.total_size + size
    consume_bytes = 0
    remain_mask = 0

    def read(self):
        elements = [
            0x10, 0x10, 7, 8
        ]
        self.bit_stream.batch_read(elements)