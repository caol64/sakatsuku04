from .bit_stream import InputBitStream
from .models import Club, MyPlayer, MyTeam, OtherTeam, OtherPlayer, PlayerAbility, Scout

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
        a = self.bit_stream.unpack_bits([0x20, 8, 5, 0x10, 1], 12)
        club.difficulty = a[2] # 007050D5
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
        for _ in range(20): # edit player, but not useful
            a = self.bit_stream.unpack_bits(0x10)
            a = self.bit_stream.unpack_str(0xd)
            # print(a.value)
            a = self.bit_stream.unpack_bits([8] * 0x15, 0x16)
            a = self.bit_stream.unpack_bits([8] * 0x2b)
            # print([hex(z.value) for z in a ])
            self.bit_stream.unpack_bits(0x10)
        self.bit_stream.unpack_bits([0x10, 4, 7], 4)
        for _ in range(0x40): # not useful
            a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        self.bit_stream.unpack_bits(0xb)
        a = self.bit_stream.unpack_str(0xd)
        self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7, 0x10, 0x10, 4, 4, 4, 4], 18)
        # 0070E584
        self.bit_stream.unpack_bits([1, 2, 4, 4, 4, 4, 7, 7, 7, 7, 7, 3, 3, 3, 3, 3], 16)
        # 0x70e595
        self.bit_stream.unpack_bits([3, 3, 3, 3, 3, 3, 4, 4, 4, 7, 4, 7, 3, 3, 7, 5, 1, 3, 4], 19)
        # 0x70e5a8
        self.bit_stream.unpack_bits([0x20, 2, 0xa, 8, 8, 0x10, 8, 3, 3, 8, 8, 8], 17)
        # 0x70e5b9
        self.bit_stream.unpack_bits([0x10] * 14)
        # 0x70e5d5
        self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10, 0x10, 0x10])
        # 0x70e5e3
        self.bit_stream.unpack_bits([4, 7, 4, 7, 6, 4, 8, 4, 0x10, 0x10, 7], 13)
        # 0x70e5f0
        self.bit_stream.unpack_bits([8] * 9)
        # 0x70e5f9
        self.bit_stream.unpack_bits([0x10, 0x10, 8, 8, 5, 5, 6, 0x20, 0x20, 0x20, 0x20, 0x10], 27)
        # 0x70e614
        for _ in range(7):
            self.bit_stream.unpack_bits([-6, 8], 2)
            self.bit_stream.unpack_bits([8] * 10)
        # 0x70e668
        self.bit_stream.unpack_bits(8)
        # 0x70e669
        self.bit_stream.align(13)
        # 0x70e676
        a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10], 10)
        # 0x70e680
        a = self.bit_stream.unpack_bits([1] * (0x19 * 0xa), 0x19 * 0xa)
        # 0x70e77a
        a = self.bit_stream.unpack_bits([7] * (0x19 * 6), 0x19 * 6)
        # 0x70e810
        a = self.bit_stream.unpack_bits([0x20] * 0x19)
        # 0x70e874
        for _ in range(0x19 + 2):
            self.bit_stream.unpack_bits([8, 8], 2)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 7, 7, 7, 0xa], 9)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 7, 7, 7, 0xa], 9)
            self.bit_stream.unpack_bits([2] * 48, 48)
        # 0x70efa0
        self.bit_stream.unpack_bits([2, 8, 6], 4)
        # 0x70efa4
        for _ in range(7):
            self.bit_stream.unpack_bits([1, 1, 0x10, 6], 6)
        # 0x70efce
        self.bit_stream.align(2)
        self.bit_stream.unpack_bits([0x20] * 2)
        # 0x70efd8
        self.bit_stream.unpack_bits([8] * (0x2e + 9))
        # 0x70f00f
        self.bit_stream.align(1)
        self.bit_stream.unpack_bits([1] * (3 + 0x2e + 21), 3 + 0x2e + 21)
        # 0x70f056
        self.bit_stream.unpack_bits([6], 2)
        self.bit_stream.unpack_bits([5, 5, 1, 1, 0x10], 7)
        # 0x70f05f
        self.bit_stream.unpack_bits([8, 0x20], 5)
        # 0x70f064
        self.bit_stream.unpack_bits([8] * 0xf)
        # 0x70f073
        self.bit_stream.unpack_bits([1] * (0x11 * 2 + 0xf), 0x11 * 2 + 0xf + 4)
        # 0x70f093
        for _ in range(0x18): # youth team players
            self.bit_stream.unpack_bits([0x10, 4, 7], 4)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x10] * 0x40)
            self.bit_stream.unpack_bits([0xb], 2)
            un = self.bit_stream.unpack_str(0xd)
            self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7], 11)
            self.bit_stream.unpack_bits([0x10, 0x10])
            self.bit_stream.unpack_bits([4, 4, 4, 4, 1, 2, 4, 4, 4, 4], 10)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4], 18)
            self.bit_stream.unpack_bits([4, 7, 4, 7, 3, 3, 7, 5, 1, 3, 4], 14)
            self.bit_stream.unpack_bits([0x20, 2], 6)
            self.bit_stream.unpack_bits([0xa, 8, 8, 0x10], 6)
            self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 8], 6)
            self.bit_stream.unpack_bits([0x10] * 14, 30)
            self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10, 0x10, 0x10, 4, 7, 4, 7, 6, 4, 8, 4], 22)
            self.bit_stream.unpack_bits([0x10, 0x10, 7])
            self.bit_stream.unpack_bits([-8] * 9, 9)
            self.bit_stream.unpack_bits([0x10, 0x10, 8, -8, 5, 5, 6], 12)
            self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 0x20, 0x10], 20)
        # 0x7126a8
        self.bit_stream.unpack_bits([-3, 3], 2)
        # 0x7126aa
        for _ in range(0x18):
            self.bit_stream.unpack_bits([7] * 6, 6)
        # 0x71273a
        self.bit_stream.align(2)
        self.bit_stream.unpack_bits([0x10, 3, 8] * (0x12 + 0x16 * 3), 4 * (0x12 + 0x16 * 3))
        # 0x71288c
        team.my_scouts = list()
        for _ in range(3): # my scout
            self.bit_stream.unpack_bits(4, 2) # index
            name = self.bit_stream.unpack_str(0xd)
            # 0x71289b
            a = self.bit_stream.unpack_bits([8, 8, 4, 7, 7, 0x10, 8], 9)
            born = a[0] # 0x71289c
            age = a[1] # 0x71289d
            un = a[2] # 0x71289e
            un = a[3] # 0x71289f
            un = a[4] # 0x7128a0
            un = a[5] # 0x7128a1
            un = a[6] # 0x7128a2
            # print([hex(z.value) for z in a ])
            # 0x7128a4
            a = self.bit_stream.unpack_bits([0x10, 4, 4, 4, 4], 6)
            # 0x7128aa
            abilities = self.bit_stream.unpack_bits([7] * 21, 21)
            # 0x7128bf
            a = self.bit_stream.unpack_bits([8, 8, 8, 0x10, 3, 3, 2], 9)
            area1 = a[0] # 0x7128c0
            area2 = a[1] # 0x7128c1
            id = a[3]
            # 0x7128c8
            for _ in range(5):
                self.bit_stream.unpack_bits([0x10, 0xb, 4, 6, 8], 8)
                self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
            self.bit_stream.unpack_bits([0xe, 4, 5, 3], 6)
            self.bit_stream.unpack_bits([8, 8, 4, 3, 0xb, 8, 0x10, 0xb, 0xb, 0xb, 0xb, 0xb], 20)
            my_scout = Scout(id, age)
            my_scout.saved_name = name
            my_scout.abilities = abilities
            my_scout.area1 = area1
            my_scout.area2 = area2
            team.my_scouts.append(my_scout)
        # 0x712a60
        team.scout_candidates = list()
        for _ in range(0xa): # スカウト候補リスト
            scout_id, offer_years, age = self.bit_stream.unpack_bits([0x10, 3, 8], 4)
            if scout_id and scout_id.value != 0xffff:
                scout = Scout(scout_id, age)
                team.scout_candidates.append(scout)
        # 0x712a88
        for _ in range(4): # coach
            self.bit_stream.unpack_bits(3, 2)
            un = self.bit_stream.unpack_str(0xd)
            self.bit_stream.unpack_bits([8, 4, 3, 8, 7, 0x10, 4, 4, 4, 4], 11)
            self.bit_stream.unpack_bits([7, 7, 7, 1, 0x10, 3, 3, 3, 3, 2, 3, 4, 8, 4, 4, 3, 2], 18)
            self.bit_stream.unpack_bits([7] * 0x35, 0x35)
            self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 14)
            self.bit_stream.unpack_bits([0x10] * 9, 20)
            self.bit_stream.unpack_bits(1, 1)
        # 0x712c98
        for _ in range(0x32):
            self.bit_stream.unpack_bits([9, 6, 6, 9, 3], 8)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x20, 0x10, 0x10, 0x10, 0x10])
            self.bit_stream.unpack_bits([0x15], 4)
            self.bit_stream.unpack_bits([0x15], 4)
            self.bit_stream.unpack_bits([0x20] * 13)
        # 0x713d00
        for _ in range(0x32):
            self.bit_stream.unpack_bits([8, 6, 8, 2], 4)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x20, 8], 12)
            self.bit_stream.unpack_bits([0x20] * 0x10)
            self.bit_stream.unpack_bits([8] * 0x10)
        # 0x714fc0
        self.bit_stream.unpack_bits([8] * (8 * 0xc))
        # 0x715020
        self.bit_stream.unpack_bits(1, 2)
        self.bit_stream.unpack_bits(4, 2)
        self.bit_stream.unpack_bits([0x10, 8, 8, 8, 1, 1, 1, 1, 1], 12)
        # 0x715030
        self.bit_stream.unpack_bits([0x20] * 0x10)
        # 0x715070
        for _ in range(7):
            self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 3, 0x10, 1, 1], 10)
        # 0x7150b6
        self.bit_stream.unpack_bits([8] * (0x20 + 0x1a))
        # 0x7150f0
        self.bit_stream.unpack_bits([0x20] * 3)
        self.bit_stream.unpack_bits(2, 2)
        self.bit_stream.unpack_bits([0x10] * 11)
        for _ in range(0x2c):
            self.bit_stream.unpack_bits([8, 3], 4)
            self.bit_stream.unpack_bits([0x20])
        # 0x715274
        for _ in range(0x36):
            self.bit_stream.unpack_bits([2, 1, 1], 3)
        # 0x715316
        self.bit_stream.unpack_bits([8] * 12)
        for _ in range(6):
            self.bit_stream.unpack_bits(8, 1)
            for _ in range(5):
                un = self.bit_stream.unpack_str(0xd)
            self.bit_stream.unpack_bits(8, 1)
        # 0x7154b4
        self.bit_stream.unpack_bits([6, 1] * 4, 8)
        for _ in range(0x27):
            self.bit_stream.unpack_bits([2, 8, 8, 1], 4)
        # 0x715558
        self.bit_stream.unpack_bits([8] * 10)
        self.bit_stream.unpack_bits([6, 1] * 4, 8)
        self.bit_stream.unpack_bits([8] * (0x27 + 6))
        self.bit_stream.align(1)
        for _ in range(0x19):
            self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        self.bit_stream.align(1)
        self.bit_stream.unpack_bits([8, 0x20, 0x20, 0x20])
        for _ in range(6):
            self.bit_stream.unpack_bits([8] * 0x16)
            self.bit_stream.unpack_bits([2, 2, 2, 5, 5, 5], 6)
            self.bit_stream.unpack_bits([0x20] * 3)
            for _ in range(0xa8 * 2):
                self.bit_stream.align(4)
                self.bit_stream.unpack_bits(-3, 4)
                for _ in range(3):
                    self.bit_stream.align(4)
                    self.bit_stream.unpack_bits([-5, -6, -5, -4], 4)
                    self.bit_stream.align(1)
                    self.bit_stream.unpack_bits([-4, -7, -7], 3)
        # 0x72b1ac
        self.bit_stream.unpack_bits([0x20] * 6)
        self.bit_stream.unpack_bits([8] * 2)
        self.bit_stream.unpack_bits([0x10] * 9)
        self.bit_stream.unpack_bits([0x20] * 9)
        for _ in range(0x1a): # 纪念相册
            un = self.bit_stream.unpack_str(0xd)
            self.bit_stream.unpack_bits([8, 4, 8, 8, 3, 4, 6, 3], 8)
            self.bit_stream.unpack_bits([8] * 18)
            self.bit_stream.unpack_bits([8] * (0x15 + 0x2b))
            self.bit_stream.unpack_bits([8, -6, 0x10], 5)
        # 0x72bcf4
        for _ in range(0x34):
            self.bit_stream.unpack_bits([0x10, 0xb], 4)
            self.bit_stream.unpack_bits([4, 6, 8], 4)
            self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
        # 0x72bfcc
        for _ in range(0x78 + 0x3c + 0x3c):
            self.bit_stream.unpack_bits([0x10, 8], 4)
        # 0x72c38c
        for _ in range(0x1a):
            self.bit_stream.unpack_bits([8], 2)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10])
        # 0x72c490
        self.bit_stream.unpack_bits([0x10] * 200)
        # 0x72c620
        for _ in range(2):
            self.bit_stream.unpack_bits([4], 2)
            un = self.bit_stream.unpack_str(0xd)
            self.bit_stream.unpack_bits([8, 8, 4, 7, 7, 0x10, 8, 0x10], 10)
            self.bit_stream.unpack_bits([4] * 4, 5)
            self.bit_stream.unpack_bits([7] * 21, 21)
            self.bit_stream.unpack_bits([8] * 3, 3)
            self.bit_stream.unpack_bits([0x10, 3, 3, 2], 6)
            for _ in range(5):
                self.bit_stream.unpack_bits([0x10, 0xb], 4)
                self.bit_stream.unpack_bits([4, 6, 8], 4)
                self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
            self.bit_stream.unpack_bits([0xe, 4, 5, 3, 8, 8, 4, 3, 0xb, 8, 0x10], 14)
            self.bit_stream.unpack_bits([0xb] * 5, 12)
        # 0x72c758
        self.bit_stream.unpack_bits([0x10, 0x10, 8], 6)
        self.bit_stream.unpack_bits([0x10] * (0xd * 3))
        self.bit_stream.unpack_bits([0x10], 4)
        self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 0x10, 0x10, 0x10])
        self.bit_stream.unpack_bits([3, 3], 2)
        self.bit_stream.unpack_bits([0x10] * 2)
        self.bit_stream.unpack_bits([0x20] * 6)
        # 0x72c7e0
        # self.print_mem_offset()
        self.bit_stream.padding(self.tail_padding)
        # 0x72c7f0
        return team

    def read_players(self) -> list[MyPlayer]:
        # 0x7051c0
        players: list[MyPlayer] = [MyPlayer(i) for i in range(0x19)]
        self.bit_stream.unpack_bits([16, 16, 1], 5)
        a = self.bit_stream.unpack_bits([-6] * 0x19, 0x19 + 2) # 7051E0
        # each player produce 0x240 bytes
        for i in range(0x19): #0x19
            players[i].id, players[i].pos, players[i].age = self.bit_stream.unpack_bits([0x10, 4, 7], 4) # 7051E4
            for l in range(0x40):
                current, current_max, max = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
                players[i].abilities.append(PlayerAbility(l, current, current_max, max)) # 705364
            self.bit_stream.unpack_bits(0xb) # unknown
            players[i].name = self.bit_stream.unpack_str(0xd)
            # print(players[i].name.value)
            a = self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7], 11) # 70537E
            players[i].born = a[0] # 705373
            players[i].born2 = a[1] # 705374
            players[i].rank = a[2] # 705375
            players[i].pos2 = a[3] # 705376
            players[i].height = a[5] # 705378
            players[i].number = a[7] # 70537A
            players[i].foot = a[8] # 70537B
            a = self.bit_stream.unpack_bits([0x10, 0x10]) # 705382
            a = self.bit_stream.unpack_bits([4, 4, 4, 4, 1, 2, 4, 4, 4, 4], 10) # 70538C
            desire = a[9] # 0x70538C
            a = self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], 16) # 70539C
            # print([hex(z.value) for z in a ])
            # players[i].un = [hex(z.value) for z in a ]
            pride = a[0] # 0x70538D
            ambition = a[1] # 0x70538E
            persistence = a[2] # 0x70538F
            un = a[3] # 0x705390
            un = a[4] # 0x705391
            players[i].tone_type = a[5] # 0x705392
            un = a[6] # 0x705393
            un = a[7] # 0x705394
            un = a[8] # 0x705395
            un = a[9] # 0x705396
            un = a[10] # 0x705397
            patient = a[11] # 0x705398
            un = a[12] # 0x705399
            un = a[13] # 0070539A
            players[i].cooperation_type = a[14] # 0x70539B
            un = a[15] # 0070539C
            players[i].grow_type_phy = self.bit_stream.unpack_bits(4, 1) # 0x70539D
            players[i].grow_type_tec = self.bit_stream.unpack_bits(4, 1) # 0x70539E
            players[i].grow_type_bra = self.bit_stream.unpack_bits(4, 1) # 0x70539F
            a = self.bit_stream.unpack_bits([7, 4, 7, 3, 3, 7, 5, 1, 3, 4], 13) # 7053AC
            players[i].style = a[6] # 0x7053A5
            a = self.bit_stream.unpack_bits([0x20, 2], 6)
            players[i].magic_value = a[0] # 7053AC a magick value contains many information
            # print(magic_value.value & 0x2000)
            a = self.bit_stream.unpack_bits([0xa, 8, 8, 0x10], 6)
            salary = a[3] # 007053B6
            # 7053B8
            a = self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 8], 6)
            offer_years_passed = a[1]
            offer_years_total = a[2]
            # 0x7053be
            a = self.bit_stream.unpack_bits([0x10] * 14, 30)
            un = a[0] # 0x7053be dissatisfied?
            tired = a[10] # 7053D2
            # 7053DC
            a = self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10, 0x10, 0x10, 4, 7, 4, 7, 6, 4, 8, 4], 22)
            un = a[0] # another magic value
            players[i].abroad_days = a[5] # 7053E8
            players[i].abroad_times = a[13] # 7053F1
            a = self.bit_stream.unpack_bits([0x10, 0x10, 7])
            a = self.bit_stream.unpack_bits([-8] * 9, 9) # not use
            # 0x705400
            a = self.bit_stream.unpack_bits([0x10, 0x10, 8, -8, 5, 5, 6], 12)
            players[i].style_equip = a[6] # 0x705408
            # 0x70540c
            a = self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 0x20, 0x10], 20)
            players[i].style_learned1 = a[0] # 0x70540c
            players[i].style_learned2 = a[1] # 0x705410
            players[i].style_learned3 = a[2] # 0x705414
            players[i].style_learned4 = a[3] # 0x705418
            un = a[4] # 0x70541a
            players[i].un = [hex(z.value) for z in a ]
            # 705420
        self.bit_stream.unpack_bits(0x10)
        for _ in range(10):
            self.bit_stream.unpack_bits([-6], 2)
            self.bit_stream.unpack_bits(0x10) # 708A4A
        self.bit_stream.unpack_bits([-6, -6, 5, -6, -6, -6, -6, -6, 2], 9)
        self.bit_stream.unpack_bits([5, 3, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3] * 3, 60)
        # 0x708a8f
        self.bit_stream.align(1)
        for _ in range(0x19): # Quarrel?
            a = self.bit_stream.unpack_bits([0x10] * 0x19)
        # 0x708f72
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
    tail_padding = b'\x7c\x01\x83\xfe' * 4

    def read(self):
        for _ in range(7):
            self.bit_stream.unpack_bits(0x20)
            for _ in range(2):
                self.bit_stream.unpack_bits(0x20)
                for _ in range(0x19):
                    self.bit_stream.unpack_bits(0xb, 2)
                self.bit_stream.align(2)
        self.bit_stream.unpack_bits(4, 4)
        self.bit_stream.padding(self.tail_padding)

class TownReader(BaseReader):
    start = LeagueReader.start + LeagueReader.size # 0x7354f0
    size = 0x17C
    total_size = LeagueReader.total_size + size
    consume_bytes = 0x20B72
    consume_bits = 0x105B8D
    remain_mask = 0x4
    tail_padding = b'\x10\xe3\xef\x1c' * 4

    def read(self):
        self.bit_stream.unpack_bits(3, 2)
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10], 10)
        self.bit_stream.unpack_bits([0x20])
        self.bit_stream.unpack_bits([7, 7, 7, 8, 8], 8)
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        for _ in range(3):
            self.bit_stream.unpack_bits([0x10, 0xe], 4)
            self.bit_stream.unpack_bits([4, 5, 3, 8], 6)
        self.bit_stream.unpack_bits([3, 4, 8], 3)
        self.bit_stream.unpack_bits([1] * 0xd, 0xd)
        self.bit_stream.unpack_bits([1] * (0x27 * 3), 0x27 * 3)
        self.bit_stream.unpack_bits([4] * 0xd, 0xd)
        self.bit_stream.unpack_bits([2] * (0x27 * 3), 0x27 * 3)
        self.bit_stream.unpack_bits([8] * 0x27, 0x27)
        self.bit_stream.unpack_bits(8, 2)
        self.bit_stream.padding(self.tail_padding)

class RecordReader(BaseReader):
    start = TownReader.start + TownReader.size # 0x73566c
    size = 0x2E310
    total_size = TownReader.total_size + size
    consume_bytes = 0x41B1F
    consume_bits = 0x20D8F6
    remain_mask = 0x2

    def read(self):
        self.bit_stream.unpack_bits([0x10, 0x10])
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
