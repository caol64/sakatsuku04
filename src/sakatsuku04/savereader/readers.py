import struct
from ..data_reader import DataReader
from ..dtos import ClubDto, MyPlayerDto, MyTeamPlayerDto, OtherTeamPlayerDto, ScoutDto, SearchDto, TownDto
from ..io import CnVer, InputBitStream, IntBitField, OutputBitStream, StrBitField
from ..objs import Player, Scout
from ..savereader.memcard_reader import MemcardReader
from ..utils import find_name_matches, get_album_bit_indices
from ..constants import scout_excl_tbl, scout_simi_excl_tbl, team_ids
from .entry_reader import EntryReader, HeadEntryReader
from .models import (
    Club,
    MyPlayer,
    MyPlayerAbility,
    MyScout,
    MyTeam,
    OtherPlayer,
    OtherTeam,
    Town,
)


class BaseReader:
    base_offset = 0x703D50

    def __init__(self, bit_stream: InputBitStream):
        self.bit_stream = bit_stream

    def print_mem_offset(self, start: int = 0):
        print(
            hex(
                self.bit_stream.unpacked_bytes_length
                + ClubReader.start
                + BaseReader.base_offset
                - start
            )
        )


class ClubReader(BaseReader):
    start = 0  # 0x703D50
    size = 0x13B4
    total_size = size
    consume_bytes = 0x127D
    consume_bits = 0x93E5
    remain_mask = 0x4
    tail_padding = b"\xec\x76\x13\x89" * 4

    def read(self) -> Club:
        club = Club()
        club.year, club.month, club.date, club.day = self.bit_stream.unpack_bits(
            [0xE, 4, 5, 3], 8
        )
        club.funds = self.bit_stream.unpack_bits(0x20) # 0x8(4)
        club.manager_name = self.bit_stream.unpack_str(0x10)  # 00703D5C 0xC(16)
        manager_name2 = self.bit_stream.unpack_str(0x10) # 0x1c(16)
        club.club_name = self.bit_stream.unpack_str(0x15) # 0x2c(21)
        a = self.bit_stream.unpack_str(0x1CB)  #  - 00703F5B 0x41(459)
        self.bit_stream.unpack_bits(3, 2)
        self.bit_stream.unpack_bits([0x10, 0x10], 6)
        self.bit_stream.unpack_bits(
            [0x20, 0xB, 1, 1, 1, 8, 8, 8, 8, 0xB, 0xB, 0xB, 0xB, 0xB, 0xB, 0xB, 0xB], 30
        )  # 0x703f82
        self.bit_stream.unpack_bits([8, 8, 8, 8, 8, 8, 8, 8, 8, 4], 14)  # 0x703f90
        self.bit_stream.unpack_bits([0x20] * 32)  # 0x704010
        for i in range(50):
            self.bit_stream.unpack_bits([0x10, 8, 8, 8], 8)
            self.bit_stream.unpack_bits([0x20] * 16)
        self.bit_stream.unpack_bits([0x20] * 48)
        for i in range(114):
            self.bit_stream.unpack_bits([0x10, 8], 4)
        # 0x7050a8
        self.bit_stream.unpack_bits(
            [0x10, 8, 8, 8, 8, 8, 8, 0x10, 8, 8, 8, 8, 8, 8, 0x10, 8, 8, 0x10, 0x10]
        )
        # 0x7050c0
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10, 0x10], 12)
        # 0x7050cc
        club.seed = self.bit_stream.unpack_bits(0x20)  # 137c(4) seed_sim
        # 0x7050d0
        seed2 = self.bit_stream.unpack_bits(0x20)  # 1380(4) seed_game
        # 0x1384
        a = self.bit_stream.unpack_bits([8, 5, 0x10, 1], 8)
        # self.print_mem_offset(0x703D50)
        club.difficulty = a[1]  # 007050D5 0x1385
        self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 8, 8], 16)
        self.bit_stream.unpack_bits([0x20, 8, 8, 8], 8)
        # 0x7050f4
        self.bit_stream.padding(self.tail_padding)
        # 0x705104
        return club


class TeamReader(BaseReader):
    start = ClubReader.start + ClubReader.size  # 0x705104
    size = 0x276EC
    total_size = ClubReader.total_size + size
    consume_bytes = 0x1836C
    consume_bits = 0xC1B5C
    remain_mask = 0x8
    tail_padding = b"\xc0\x89\x3f\x76" * 4

    def read(self) -> MyTeam:
        team = MyTeam()
        self.bit_stream.unpack_bits([8, 1, 1], 4)
        self.bit_stream.unpack_bits(16)
        self.bit_stream.unpack_bits([8] * 40)
        team.english_name = self.bit_stream.unpack_str(0x20)
        self.bit_stream.unpack_bits([8] * 57)
        team.oilis_english_name = self.bit_stream.unpack_str(0x20)
        self.bit_stream.unpack_bits([8] * 15)
        self.bit_stream.unpack_bits([16, 16, 8, 8])  # 7051BF
        team.players = self.read_players()
        self.read_players()
        # 0070DD78
        for _ in range(20):  # edit player, but not useful
            a = self.bit_stream.unpack_bits(0x10)
            a = self.bit_stream.unpack_str(0xD)
            # print(a.value)
            a = self.bit_stream.unpack_bits([8] * 0x15, 0x16)
            a = self.bit_stream.unpack_bits([8] * 0x2B)
            # print([hex(z.value) for z in a ])
            self.bit_stream.unpack_bits(0x10)
        self.bit_stream.unpack_bits([0x10, 4, 7], 4)
        for _ in range(0x40):  # not useful
            a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        self.bit_stream.unpack_bits(0xB)
        a = self.bit_stream.unpack_str(0xD)
        self.bit_stream.unpack_bits(
            [8, 8, 4, 4, 7, 8, 4, 7, 3, 7, 0x10, 0x10, 4, 4, 4, 4], 18
        )
        # 0070E584
        self.bit_stream.unpack_bits(
            [1, 2, 4, 4, 4, 4, 7, 7, 7, 7, 7, 3, 3, 3, 3, 3], 16
        )
        # 0x70e595
        self.bit_stream.unpack_bits(
            [3, 3, 3, 3, 3, 3, 4, 4, 4, 7, 4, 7, 3, 3, 7, 5, 1, 3, 4], 19
        )
        # 0x70e5a8
        self.bit_stream.unpack_bits([0x20, 2, 0xA, 8, 8, 0x10, 8, 3, 3, 8, 8, 8], 17)
        # 0x70e5b9
        self.bit_stream.unpack_bits([0x10] * 14)
        # 0x70e5d5
        self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10, 0x10, 0x10])
        # 0x70e5e3
        self.bit_stream.unpack_bits([4, 7, 4, 7, 6, 4, 8, 4, 0x10, 0x10, 7], 13)
        # 0x70e5f0
        self.bit_stream.unpack_bits([8] * 9)
        # 0x70e5f9
        self.bit_stream.unpack_bits(
            [0x10, 0x10, 8, 8, 5, 5, 6, 0x20, 0x20, 0x20, 0x20, 0x10], 27
        )
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
        a = self.bit_stream.unpack_bits([1] * (0x19 * 0xA), 0x19 * 0xA)
        # 0x70e77a
        a = self.bit_stream.unpack_bits([7] * (0x19 * 6), 0x19 * 6)
        # 0x70e810
        a = self.bit_stream.unpack_bits([0x20] * 0x19)
        # 0x70e874
        for _ in range(0x19 + 2):
            self.bit_stream.unpack_bits([8, 8], 2)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 7, 7, 7, 0xA], 9)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 7, 7, 7, 0xA], 9)
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
        self.bit_stream.unpack_bits([8] * (0x2E + 9))
        # 0x70f00f
        self.bit_stream.align(1)
        self.bit_stream.unpack_bits([1] * (3 + 0x2E + 21), 3 + 0x2E + 21)
        # 0x70f056
        self.bit_stream.unpack_bits([6], 2)
        self.bit_stream.unpack_bits([5, 5, 1, 1, 0x10], 7)
        # 0x70f05f
        self.bit_stream.unpack_bits([8, 0x20], 5)
        # 0x70f064
        self.bit_stream.unpack_bits([8] * 0xF)
        # 0x70f073
        self.bit_stream.unpack_bits([1] * (0x11 * 2 + 0xF), 0x11 * 2 + 0xF + 4)
        # 0x70f0a8
        team.youth_players = self._read_my_players(0x18)
        # 0x7126a8
        self.bit_stream.unpack_bits([-3, 3], 2)
        # 0x7126aa
        for _ in range(0x18):
            self.bit_stream.unpack_bits([7] * 6, 6)
        # 0x71273a
        self.bit_stream.align(2)
        # 0x71273c 教练list d638
        self.bit_stream.unpack_bits(
            [0x10, 3, 8] * (0x12 + 0x16 * 3), 4 * (0x12 + 0x16 * 3)
        )
        # 0x71288c d788 球探list
        team.my_scouts = list()
        for _ in range(3):
            self.bit_stream.unpack_bits(4, 2)  # index
            name = self.bit_stream.unpack_str(0xD) # 2(d)
            # 0x71289b
            a = self.bit_stream.unpack_bits([8, 8, 4, 7, 7, 0x10, 8], 9)
            born = a[0]  # 0x71289c
            age = a[1]  # 0x71289d
            un = a[2]  # 0x71289e
            un = a[3]  # 0x71289f
            un = a[4]  # 0x7128a0
            un = a[5]  # 0x7128a1
            un = a[6]  # 0x7128a2
            # print([hex(z.value) for z in a ])
            # 0x7128a4
            a = self.bit_stream.unpack_bits([0x10, 4, 4, 4, 4], 6)
            # 0x7128aa
            abilities = self.bit_stream.unpack_bits([7] * 21, 21)
            # 0x7128bf
            a = self.bit_stream.unpack_bits([8, 8, 8, 0x10, 3, 3, 2], 9)
            area1 = a[0]  # 0x7128c0 0x33(1)
            area2 = a[1]  # 0x7128c1 0x34(1)
            id = a[3]  # 0x7128c3 0x36(2)
            # 0x7128c8
            for _ in range(5):
                self.bit_stream.unpack_bits([0x10, 0xB, 4, 6, 8], 8)
                self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
            self.bit_stream.unpack_bits([0xE, 4, 5, 3], 6)
            self.bit_stream.unpack_bits(
                [8, 8, 4, 3, 0xB, 8, 0x10, 0xB, 0xB, 0xB, 0xB, 0xB], 20
            )
            my_scout = MyScout(id, age)
            my_scout.saved_name = name
            my_scout.abilities = abilities
            my_scout.area1 = area1
            my_scout.area2 = area2
            team.my_scouts.append(my_scout)
        # 0x712a60
        team.scout_candidates = list()
        for _ in range(0xA):  # スカウト候補リスト
            scout_id, offer_years, age = self.bit_stream.unpack_bits([0x10, 3, 8], 4)
            if scout_id and scout_id.value != 0xFFFF:
                scout = MyScout(scout_id, age)
                team.scout_candidates.append(scout)
        # 0x712a88
        for _ in range(4):  # coach
            self.bit_stream.unpack_bits(3, 2)
            un = self.bit_stream.unpack_str(0xD)
            self.bit_stream.unpack_bits([8, 4, 3, 8, 7, 0x10, 4, 4, 4, 4], 11)
            self.bit_stream.unpack_bits(
                [7, 7, 7, 1, 0x10, 3, 3, 3, 3, 2, 3, 4, 8, 4, 4, 3, 2], 18
            )
            self.bit_stream.unpack_bits([7] * 0x35, 0x35)
            self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 14)
            self.bit_stream.unpack_bits([0x10] * 9, 20)
            self.bit_stream.unpack_bits(1, 1)
        # 0x712c98
        for _ in range(50):
            self.bit_stream.unpack_bits([9, 6, 6, 9, 3], 8)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x20, 0x10, 0x10, 0x10, 0x10])
            self.bit_stream.unpack_bits([0x15], 4)
            self.bit_stream.unpack_bits([0x15], 4)
            self.bit_stream.unpack_bits([0x20] * 13)
        # 0x713d00
        for _ in range(50):
            self.bit_stream.unpack_bits([8, 6, 8, 2], 4)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x20, 8], 12)
            self.bit_stream.unpack_bits([0x20] * 0x10)
            self.bit_stream.unpack_bits([8] * 0x10)
        # 0x714fc0
        self.bit_stream.unpack_bits([8] * (8 * 12))
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
        self.bit_stream.unpack_bits([8] * (0x20 + 0x1A))
        # 0x7150f0
        self.bit_stream.unpack_bits([0x20] * 3)
        self.bit_stream.unpack_bits(2, 2)
        self.bit_stream.unpack_bits([0x10] * 11)
        for _ in range(44):
            self.bit_stream.unpack_bits([8, 3], 4)
            self.bit_stream.unpack_bits([0x20])
        # 0x715274
        for _ in range(54):
            self.bit_stream.unpack_bits([2, 1, 1], 3)
        # 0x715316
        self.bit_stream.unpack_bits([8] * 12)
        for _ in range(6):
            self.bit_stream.unpack_bits(8, 1)
            for _ in range(5):
                un = self.bit_stream.unpack_str(0xD)
            self.bit_stream.unpack_bits(8, 1)
        # 0x7154b4
        self.bit_stream.unpack_bits([6, 1] * 4, 8)
        for _ in range(39):
            self.bit_stream.unpack_bits([2, 8, 8, 1], 4)
        # 0x715558
        self.bit_stream.unpack_bits([8] * 10)
        self.bit_stream.unpack_bits([6, 1] * 4, 8)
        self.bit_stream.unpack_bits([8] * (39 + 6))
        self.bit_stream.align(1)
        for _ in range(25):
            self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        self.bit_stream.align(1)
        self.bit_stream.unpack_bits([8, 0x20, 0x20, 0x20])
        for _ in range(6):
            self.bit_stream.unpack_bits([8] * 22)
            self.bit_stream.unpack_bits([2, 2, 2, 5, 5, 5], 6)
            self.bit_stream.unpack_bits([0x20] * 3)
            for _ in range(0xA8 * 2):
                self.bit_stream.align(4)
                self.bit_stream.unpack_bits(-3, 4)
                for _ in range(3):
                    self.bit_stream.align(4)
                    self.bit_stream.unpack_bits([-5, -6, -5, -4], 4)
                    self.bit_stream.align(1)
                    self.bit_stream.unpack_bits([-4, -7, -7], 3)
        # 0x72b1ac 0x260a8
        self.bit_stream.unpack_bits([0x20] * 6)
        self.bit_stream.unpack_bits([8] * 2)
        # 0x260c2
        self.bit_stream.unpack_bits([0x10] * 9)
        # self.print_mem_offset(0x705104)
        # 0x260d4
        team.album_players = self.bit_stream.unpack_bits([0x20] * 9) # 图鉴球员
        # 0x72b1fc 0x260f8
        for _ in range(26):  # 纪念相册
            un = self.bit_stream.unpack_str(0xD)
            self.bit_stream.unpack_bits([8, 4, 8, 8, 3, 4, 6, 3], 8)
            self.bit_stream.unpack_bits([8] * 18)
            self.bit_stream.unpack_bits([8] * (0x15 + 0x2B))
            self.bit_stream.unpack_bits([8, -6, 0x10], 5)
        # 0x72bcf4 自由球员
        for _ in range(52):
            self.bit_stream.unpack_bits([0x10, 0xB], 4)
            self.bit_stream.unpack_bits([4, 6, 8], 4)
            self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
        # 0x72bfcc
        for _ in range(240):
            self.bit_stream.unpack_bits([0x10, 8], 4)
        # 0x72c38c 0x27288
        for _ in range(26):
            self.bit_stream.unpack_bits([8], 2)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10])
        # 0x72c490
        self.bit_stream.unpack_bits([0x10] * 200)
        # 0x72c620
        for _ in range(2):
            self.bit_stream.unpack_bits([4], 2)
            un = self.bit_stream.unpack_str(0xD)
            self.bit_stream.unpack_bits([8, 8, 4, 7, 7, 0x10, 8, 0x10], 10)
            self.bit_stream.unpack_bits([4] * 4, 5)
            self.bit_stream.unpack_bits([7] * 21, 21)
            self.bit_stream.unpack_bits([8] * 3, 3)
            self.bit_stream.unpack_bits([0x10, 3, 3, 2], 6)
            for _ in range(5):
                self.bit_stream.unpack_bits([0x10, 0xB], 4)
                self.bit_stream.unpack_bits([4, 6, 8], 4)
                self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
            self.bit_stream.unpack_bits([0xE, 4, 5, 3, 8, 8, 4, 3, 0xB, 8, 0x10], 14)
            self.bit_stream.unpack_bits([0xB] * 5, 12)
        # 0x72c758
        self.bit_stream.unpack_bits([0x10, 0x10, 8], 6)
        self.bit_stream.unpack_bits([0x10] * (0xD * 3))
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

    def _read_my_players(self, count: int) -> list[MyPlayer]:
        players: list[MyPlayer] = [MyPlayer(i) for i in range(count)]
        # each player produce 0x240 bytes
        # 0x7051E0
        for i in range(count):
            players[i].id, players[i].pos, players[i].age = self.bit_stream.unpack_bits(
                [0x10, 4, 7], 4
            )  # 7051E4
            for ll in range(0x40):
                current, current_max, max = self.bit_stream.unpack_bits(
                    [0x10, 0x10, 0x10]
                )
                players[i].abilities.append(
                    MyPlayerAbility(ll, current, current_max, max)
                )  # 705364
            self.bit_stream.unpack_bits(0xB)  # pop?
            players[i].name = self.bit_stream.unpack_str(0xD)  # 705364 186(13)
            # print(players[i].name.value)
            a = self.bit_stream.unpack_bits(
                [8, 8, 4, 4, 7, 8, 4, 7, 3, 7], 11
            )  # 70537E
            players[i].born = a[0]  # 705373 193
            players[i].born2 = a[1]  # 705374 194
            players[i].rank = a[2]  # 705375 195
            players[i].base_pos = a[3]  # 705376 196 (base pos)
            # 197 base age
            players[i].height = a[5]  # 705378 198(2)
            players[i].number = a[7]  # 70537A 19a
            players[i].foot = a[8]  # 70537B 19b
            # 70537E
            # self.print_mem_offset(0x7051e0)
            a = self.bit_stream.unpack_bits([0x10, 0x10])  # 19e(2) 1a0(2)
            # 705382
            a = self.bit_stream.unpack_bits([4, 4, 4, 4, 1, 2, 4, 4, 4, 4], 10)
            players[i].desire = a[9]  # 0x70538B 1ab
            # 70538C
            a = self.bit_stream.unpack_bits(
                [7, 7, 7, 7, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], 16
            )
            players[i].pride = a[0]  # 0x70538C 1ac
            players[i].ambition = a[1]  # 0x70538D 1ad
            players[i].persistence = a[2]  # 0x70538E 1ae
            un = a[3]  # 0x70538F
            un = a[4]  # 0x705390
            players[i].tone_type = a[5]  # 0x705391 1b1
            un = a[6]  # 0x705392
            un = a[7]  # 0x705393
            un = a[8]  # 0x705394
            un = a[9]  # 0x705395
            un = a[10]  # 0x705396
            players[i].patient = a[11]  # 0x705397 1b7
            un = a[12]  # 0x705398
            un = a[13]  # 00705399
            players[i].cooperation_type = a[14]  # 0x70539A 1ba
            players[i].grow_type_id = a[15]  # 0x70539B 1bb
            # 70539C
            players[i].grow_type_phy = self.bit_stream.unpack_bits(4, 1)  # 0x70539C 1bc
            players[i].grow_type_tec = self.bit_stream.unpack_bits(4, 1)  # 0x70539D 1bd
            players[i].grow_type_sys = self.bit_stream.unpack_bits(4, 1)  # 0x70539E 1be
            a = self.bit_stream.unpack_bits([7, 4, 7, 3, 3, 7], 6)
            players[i].style = self.bit_stream.unpack_bits(5, 1)  # 0x7053a5 1c5
            a = self.bit_stream.unpack_bits([1, 3, 4], 6)
            # 0x7053ac
            a = self.bit_stream.unpack_bits([0x20, 2], 6)
            players[i].magic_value = a[0]  # 0x7053ac 1cc(4)
            # 0x7053B2
            a = self.bit_stream.unpack_bits([0xA, 8, 8, 0x10], 6)
            tired1 = a[0]  # 0x7053B2 1d2(2)
            players[i].salary = a[3]  # 0x7053B6 1d6(2)
            # 7053B8
            a = self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 8], 6)
            joined_years = a[0] # 0x7053B8 1d8(1)
            players[i].offer_years_passed = a[1]  # 0x7053B9 1d9(1)
            players[i].offer_years_total = a[2]  # 0x7053B9A 1da(1)
            contract_cond = a[3] # 0x7053B9B 1db(1)
            # 0x7053be
            a = self.bit_stream.unpack_bits([0x10] * 14, 30)
            comp = a[0]  # 0x7053be 1de(2) 不满
            tired = a[10]  # 0x7053D2 1f2(2)
            # 7053DC
            a = self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10])
            power = a[3] # 0x7053e4 204(2) 气力，max=1000
            # 0x7053e6
            a = self.bit_stream.unpack_bits([0x10, 0x10, 4, 7, 4, 7, 6, 4, 8, 4], 12)
            un = a[0]  # 0x7053e6 206(2)
            players[i].injury_days = a[1]  # 0x7053e8 208(2)
            players[i].abroad_times = a[9]  # 0x7053f1 211(1)
            # 0x7053f2
            a = self.bit_stream.unpack_bits([0x10, 0x10, 7])
            captain_exp = a[0]  # 0x7053f2 212(2)
            keyman_exp = a[1]  # 0x7053f4 214(2)
            a = self.bit_stream.unpack_bits([-8] * 9, 9)  # not use
            # 0x705400
            a = self.bit_stream.unpack_bits([0x10, 0x10, 8, -8, 5, 5, 6], 12)
            a[0]  # 0x705400 220(2)
            a[1]  # 0x705402 222(2)
            a[2]  # 0x705404 224(1) 能力爆发（强度）
            a[3]  # 0x705405 225(1) 能力爆发（倒计时）为0爆发
            a[4]  # 0x705406 226(1)
            a[5]  # 0x705407 227(1) 能力爆发（原因）
            players[i].style_equip = a[6]  # 0x705408 228(4)
            # 0x70540c
            a = self.bit_stream.unpack_bits([0x20, 0x20, 0x20, 0x20, 0x10], 20)
            players[i].style_learned1 = a[0]  # 0x70540c 22c(4)
            players[i].style_learned2 = a[1]  # 0x705410 230(4)
            players[i].style_learned3 = a[2]  # 0x705414 234(4)
            players[i].style_learned4 = a[3]  # 0x705418 238(4)
            un = a[4]  # 0x70541c 23c(4)
            # 705420
        return players

    def read_players(self) -> list[MyPlayer]:
        # 0x7051c0
        self.bit_stream.unpack_bits([16, 16, 1], 5)
        a = self.bit_stream.unpack_bits([-6] * 0x19, 0x19 + 2)
        # 0x7051e0
        players = self._read_my_players(0x19)
        self.bit_stream.unpack_bits(0x10)
        for _ in range(10):
            self.bit_stream.unpack_bits([-6], 2)
            self.bit_stream.unpack_bits(0x10)  # 708A4A
        self.bit_stream.unpack_bits([-6, -6, 5, -6, -6, -6, -6, -6, 2], 9)
        self.bit_stream.unpack_bits(
            [5, 3, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3] * 3, 60
        )
        # 0x708a8f
        self.bit_stream.align(1)
        for _ in range(0x19):  # Quarrel?
            a = self.bit_stream.unpack_bits([0x10] * 0x19)
        # 0x708f72
        self.bit_stream.unpack_bits([8] * 3)
        a = self.bit_stream.unpack_bits([8] * 0x19)
        self.bit_stream.unpack_bits(3, 2)
        coach_name = self.bit_stream.unpack_str(0xD)  # coach name
        a = self.bit_stream.unpack_bits(
            [
                8,
                4,
                3,
                8,
                7,
                0x10,
                4,
                4,
                4,
                4,
                7,
                7,
                7,
                1,
                -0x10,
                3,
                3,
                3,
                3,
                2,
                3,
                4,
                8,
                4,
                4,
                3,
                2,
            ],
            29,
        )  # 708FBA
        a = self.bit_stream.unpack_bits([7] * 0x35, 0x35)
        # print([z.value for z in a ])
        self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 15)
        self.bit_stream.unpack_bits([0x10] * 9)
        self.bit_stream.unpack_bits(1, 2)
        self.bit_stream.unpack_bits([3, 1], 2)
        for _ in range(0xC):
            self.bit_stream.unpack_bits([8, 8, 1, 1], 4)
            self.bit_stream.unpack_bits([1] * 0x19, 0x19)
            self.bit_stream.unpack_bits([8, 5, 5, 8, 3] * 12, 5 * 12)
        self.bit_stream.unpack_bits([8, 3] * (0x19 * 0xC), 2 * (0x19 * 0xC))
        for _ in range(7):
            self.bit_stream.unpack_bits(8)
            for _ in range(3):
                self.bit_stream.unpack_bits([-6, 8], 2)
                self.bit_stream.unpack_bits([8] * 0xA)
        self.bit_stream.unpack_bits(8)
        return players


class OtherTeamReader(BaseReader):
    start = TeamReader.start + TeamReader.size  # 0x72c7f0
    size = 0x89C0
    total_size = TeamReader.total_size + size
    consume_bytes = 0x208B5
    consume_bits = 0x1045A2
    remain_mask = 0x20
    tail_padding = b"\x40\x03\xbf\xfc" * 4

    def read(self) -> list[OtherTeam]:
        teams: list[OtherTeam] = list()
        for i in range(0x109):  # loop the teams
            id = self.bit_stream.unpack_bits(0x10)
            players: list[OtherPlayer] = list()
            for _ in range(0x19):  # loop the playes
                pid, age, ability_graph = self.bit_stream.unpack_bits([0x10, 7, 8], 4)
                player = OtherPlayer(pid, age, ability_graph)
                players.append(player)
            unknown1, unknown2, friendly = self.bit_stream.unpack_bits(
                [0x10, 0x10, 7], 6
            )  # 72c856 - 72c85b
            other_team = OtherTeam(i, id, friendly, unknown1, unknown2, players)
            teams.append(other_team)
        # 7337bc
        for i in range(0x109):
            for j in range(0x19):
                teams[i].players[j].number = self.bit_stream.unpack_bits(8)  # 背番号
        # 73519d
        self.bit_stream.unpack_bits([8, 8], 3)
        # 0x7351a0
        self.bit_stream.padding(self.tail_padding)
        return teams


class LeagueReader(BaseReader):
    start = OtherTeamReader.start + OtherTeamReader.size  # 0x7351b0
    size = 0x340
    total_size = OtherTeamReader.total_size + size
    consume_bytes = 0x20AEA
    consume_bits = 0x105750
    remain_mask = 0x80
    tail_padding = b"\x7c\x01\x83\xfe" * 4

    def read(self):
        for _ in range(7):
            self.bit_stream.unpack_bits(0x20)
            for _ in range(2):
                self.bit_stream.unpack_bits(0x20)
                for _ in range(0x19):
                    self.bit_stream.unpack_bits(0xB, 2)
                self.bit_stream.align(2)
        self.bit_stream.unpack_bits(4, 4)
        self.bit_stream.padding(self.tail_padding)


class TownReader(BaseReader):
    start = LeagueReader.start + LeagueReader.size  # 0x7354f0
    size = 0x17C
    total_size = LeagueReader.total_size + size
    consume_bytes = 0x20B72
    consume_bits = 0x105B8D
    remain_mask = 0x4
    tail_padding = b"\x10\xe3\xef\x1c" * 4

    def read(self) -> Town:
        town = Town()
        self.bit_stream.unpack_bits(3, 2) # 0, 1
        a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10], 10)
        town.living = a[0] # 2(2)
        town.economy = a[1] # 4(2)
        town.sports = a[2] # 6(2)
        town.env = a[3] # 8(2)
        # 0xb
        town.population = self.bit_stream.unpack_bits(0x20) # 0xc(4)
        # 0xf
        a = self.bit_stream.unpack_bits([7, 7, 7, 8, 8], 8)
        town.price = a[0] # 0x10
        town.traffic_level = a[1] # 0x11
        town.soccer_pop = a[2] # 0x12
        # print(population.value)
        # 0x18
        a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        town.soccer_level = a[2] # 0x1c(2)
        # 0x1e
        for _ in range(3): # 姐妹都市
            self.bit_stream.unpack_bits([0x10, 0xE], 4)
            self.bit_stream.unpack_bits([4, 5, 3, 8], 6)
        self.bit_stream.unpack_bits([3, 4, 8], 3)
        self.bit_stream.unpack_bits([1] * 0xD, 13)
        self.bit_stream.unpack_bits([1] * (0x27 * 3), 117)
        self.bit_stream.unpack_bits([4] * 0xD, 13)
        self.bit_stream.unpack_bits([2] * (0x27 * 3), 117)
        self.bit_stream.unpack_bits([8] * 0x27, 39)
        self.bit_stream.unpack_bits(8, 2)
        self.bit_stream.padding(self.tail_padding)
        return town


class RecordReader(BaseReader):
    start = TownReader.start + TownReader.size  # 0x73566c
    size = 0x2E310
    total_size = TownReader.total_size + size
    consume_bytes = 0x41B1F
    consume_bits = 0x20D8F6
    remain_mask = 0x2

    def read(self):
        self.bit_stream.unpack_bits([0x10, 0x10])
        self.bit_stream.skip(
            RecordReader.consume_bits,
            RecordReader.total_size - self.bit_stream.unpacked_bytes_length,
        )


class ScheReader(BaseReader):
    start = RecordReader.start + RecordReader.size
    size = 0xA14
    total_size = RecordReader.total_size + size
    consume_bytes = 0x4221F
    consume_bits = 0x2110F8
    remain_mask = 0x2
    tail_padding = b"\x38\x00\xc7\xff" * 4

    def read(self):
        # 0x76397c
        for _ in range(28):
            self.bit_stream.unpack_bits(5, 1)
        # 0x763998 0x1c
        for _ in range(28):
            self.bit_stream.unpack_bits(5, 1)
        # 0x7639b4 0x38
        for _ in range(106):
            self.bit_stream.unpack_bits(1, 1)
            self.bit_stream.unpack_bits(4, 1)
            self.bit_stream.unpack_bits(0x10)
            self.bit_stream.unpack_bits(7, 1)
            self.bit_stream.unpack_bits(2, 1)
            self.bit_stream.unpack_bits(2, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(0xb, 2)
            self.bit_stream.unpack_bits(0xb, 2)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(0x10)
        # 0x764128 0x7ac
        for _ in range(4):
            self.bit_stream.unpack_bits(0xe, 2)
            self.bit_stream.unpack_bits(0x4, 1)
            self.bit_stream.unpack_bits(0x5, 1)
            self.bit_stream.unpack_bits(0x3, 2)
            self.bit_stream.unpack_bits(0x10)
            self.bit_stream.unpack_bits(0x5, 2)
            self.bit_stream.unpack_bits(0xb, 2)
            self.bit_stream.unpack_bits(0xb, 2)
            self.bit_stream.unpack_bits(0xb, 2)
        # 0x764168 0x7ec
        for _ in range(64):
            self.bit_stream.unpack_bits(0x1, 1)
        # 0x7641a8 0x82c
        for _ in range(32):
            self.bit_stream.unpack_bits(0x1, 1)
        # 0x7641c8 0x84c # 留学地list
        for _ in range(70):
            a = self.bit_stream.unpack_bits(0x2, 2)
            b = self.bit_stream.unpack_bits(0x10)
            # print(a.value, b.value)
        # print("===========")
        # 0x7642e0 0x964 # 集训地list
        for _ in range(40):
            a = self.bit_stream.unpack_bits(0x2, 2)
            b = self.bit_stream.unpack_bits(0x10)
            # print(a.value, b.value)
        # self.print_mem_offset(0x76397c)
        # 0x764380 0xa04
        self.bit_stream.padding(self.tail_padding)


class OptionReader(BaseReader):
    start = ScheReader.start + ScheReader.size
    size = 0x38
    total_size = ScheReader.total_size + size
    consume_bytes = 0x42237
    consume_bits = 0x2111B8
    remain_mask = 0x40

    def read(self):
        self.bit_stream.unpack_bits(0x20)
        for _ in range(0xD):
            self.bit_stream.unpack_bits(1, 4)

        # self.bit_stream.skip(OptionReader.consume_bits, OptionReader.total_size - self.bit_stream.unpacked_bytes_length)


class MailReader(BaseReader):
    start = OptionReader.start + OptionReader.size
    size = 0x1
    total_size = OptionReader.total_size + size
    consume_bytes = 0
    remain_mask = 0

    def read(self):
        elements = [0x10, 0x10, 7, 8]
        self.bit_stream.batch_read(elements)


class SaveDataReader(DataReader):
    def __init__(self, file_path: str):
        self.path = file_path
        mc_reader = MemcardReader(file_path)
        save_entries = mc_reader.read_save_entries()
        self.save_entries = {item.name: item for item in save_entries}
        self.entry_reader: EntryReader = None
        self.out_bit_stream: OutputBitStream = None
        self.selected_game: str = None
        self.club: Club = None
        self.my_team: MyTeam = None
        self.other_teams: list[OtherTeam] = None
        self.town: Town = None

    def games(self) -> list[str]:
        return list(self.save_entries.keys())

    def select_game(self, game: str):
        self.selected_game = game
        save_entry = self.save_entries.get(game)
        self.entry_reader = EntryReader(save_entry.main_save_entry)
        self.entry_reader.check_crc()
        self.entry_reader.dec()
        decoded_byte_array = self.entry_reader.decoded_data()
        in_bit_stream = InputBitStream(decoded_byte_array)
        self.out_bit_stream = OutputBitStream(decoded_byte_array)
        club_reader = ClubReader(in_bit_stream)
        self.club = club_reader.read()
        team_reader = TeamReader(in_bit_stream)
        self.my_team = team_reader.read()
        oteam_reader = OtherTeamReader(in_bit_stream)
        self.other_teams = oteam_reader.read()
        leager_reader = LeagueReader(in_bit_stream)
        leager_reader.read()
        town_reader = TownReader(in_bit_stream)
        self.town = town_reader.read()
        record_reader = RecordReader(in_bit_stream)
        record_reader.read()
        sche_reader = ScheReader(in_bit_stream)
        sche_reader.read()
        CnVer.set_ver(self.game_ver())
        Player.reset_player_dict()
        Scout.reset_scout_dict()

    def read_club(self) -> ClubDto:
        if not self.selected_game:
            return None
        return self.club.to_dto()

    def read_myteam(self) -> list[MyPlayerDto]:
        result = []
        for player in sorted(
            filter(lambda player: player.id.value != 0xFFFF, self.my_team.players),
            key=lambda player: player.pos.value,
        ):
            result.append(
                MyTeamPlayerDto(
                    id=player.id.value, name=player.name.value, pos=player.pos.value
                )
            )
        return result

    def read_youth_team(self) -> list[MyPlayerDto]:
        result = []
        for player in sorted(
            filter(
                lambda player: player.id.value != 0xFFFF, self.my_team.youth_players
            ),
            key=lambda player: player.pos.value,
        ):
            result.append(
                MyTeamPlayerDto(
                    id=player.id.value, name=player.name.value, pos=player.pos.value
                )
            )
        return result

    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        team = self.other_teams[team_index]
        result = []
        for player in [player for player in team.players if player.id.value != 0xFFFF]:
            result.append(player.to_dto())
        return sorted(result, key=lambda player: player.pos)

    def read_other_team_friendly(self, team_index: int) -> int:
        team = self.other_teams[team_index]
        return team.friendly.value

    def read_myplayer(self, id: int, team: int) -> MyPlayerDto:
        if team == 0:
            player = list(
                filter(lambda p: p.id.value == id, self.my_team.players)
            ).pop()
        else:
            player = list(
                filter(lambda p: p.id.value == id, self.my_team.youth_players)
            ).pop()
        return player.to_dto()

    def search_player(self, data: SearchDto) -> list[OtherTeamPlayerDto]:
        name = data.name
        pos = data.pos
        age = data.age
        country = data.country
        tone = data.tone
        cooperation = data.cooperation
        rank = data.rank
        ids = []
        for team in self.other_teams:
            for player in team.players:
                if player.id.value != 0xFFFF:
                    if age and age != player.age.value:
                        continue
                    ids.append(player.id.value)
        filter_players = {k: v for k, v in Player.player_dict().items() if k in ids}
        filter_ids = find_name_matches(filter_players, name) if name else ids
        result = []
        for i, team in enumerate(self.other_teams):
            for player in team.players:
                if player.id.value in filter_ids:
                    dto = player.to_dto()
                    if pos is not None and pos != dto.pos:
                        continue
                    if country is not None and (
                        (country == 50 and dto.born > 50)
                        or (country != 50 and dto.born != country)
                    ):
                        continue
                    if tone is not None and tone != dto.tone_type:
                        continue
                    if cooperation is not None and cooperation != dto.cooperation_type:
                        continue
                    if rank is not None and rank != dto.rank:
                        continue
                    dto.team_index = i
                    result.append(dto)
        return result

    def read_town(self) -> TownDto:
        return self.town.to_dto()

    def read_my_album_players(self) -> list[int]:
        players_raw = [p.value for p in self.my_team.album_players]
        byte_data = bytearray()
        for val in players_raw:
            byte_data.extend(struct.pack('<I', val))
        return get_album_bit_indices(byte_data)

    def read_scouts(self, type: int) -> list[ScoutDto]:
        scouts = (
            [f.to_dto() for f in self.my_team.my_scouts]
            if type == 0
            else [f.to_dto_with_name(f.id.value) for f in self.my_team.scout_candidates]
        )

        if not scouts:
            return scouts

        def resolve_players(player_ids: list[int]) -> list[SearchDto]:
            result = []
            for pid in player_ids:
                dto = SearchDto(name=Player(pid).name)
                for team in self.other_teams:
                    for player in team.players:
                        if player.id.value == pid:
                            dto.age = player.age.value
                            dto.team_id = team_ids.index(team.id.value)
                            break
                result.append(dto)
            return result

        for scout in scouts:
            scout.exclusive_players = resolve_players(scout_excl_tbl.get(scout.id, []))
            scout.simi_exclusive_players = resolve_players(scout_simi_excl_tbl.get(scout.id, []))

        return scouts


    def save_club(self, club_data: ClubDto) -> bool:
        save_entry = self.save_entries.get(self.selected_game)
        self.club.funds.value = club_data.combo_funds()
        self.club.year.value = club_data.year + 2003
        self.club.difficulty.value = club_data.difficulty
        bits_fields = list()
        bits_fields.append(self.club.funds)
        bits_fields.append(self.club.year)
        bits_fields.append(self.club.difficulty)
        head_reader = HeadEntryReader(save_entry.save_head_entry)
        head_reader.check_crc()
        head = head_reader.read()
        head.year.value = club_data.year + 2003
        head_reader.write(head.year)
        head_bytes = head_reader.build_save_bytes()
        self._save(bits_fields, head_bytes)
        return True

    def save_player(self, data: MyPlayerDto, team: int) -> bool:
        player = list(
            filter(lambda p: p.id.value == data.id, self.my_team.players)
        ).pop() if team == 0 else list(
            filter(lambda p: p.id.value == data.id, self.my_team.youth_players)
        ).pop()
        if player:
            player.age.value = data.age
            player.abroad_times.value = data.abroad_times
            player.born.value = data.born
            player.born2.value = data.born
            player.pos.value = data.pos
            player.style.value = data.style
            player.style_equip.value = data.style
            player.set_style(data.style)
            player.cooperation_type.value = data.cooperation_type
            player.tone_type.value = data.tone_type
            player.grow_type_phy.value = data.grow_type_phy
            player.grow_type_tec.value = data.grow_type_tec
            player.grow_type_sys.value = data.grow_type_sys
            player.salary.value = data.combo_salary()
            bits_fields = list()
            bits_fields.append(player.age)
            bits_fields.append(player.abroad_times)
            bits_fields.append(player.born)
            bits_fields.append(player.born2)
            bits_fields.append(player.pos)
            bits_fields.append(player.style)
            bits_fields.append(player.style_equip)
            bits_fields.append(player.style_learned1)
            bits_fields.append(player.style_learned2)
            bits_fields.append(player.cooperation_type)
            bits_fields.append(player.tone_type)
            bits_fields.append(player.grow_type_phy)
            bits_fields.append(player.grow_type_tec)
            bits_fields.append(player.grow_type_sys)
            bits_fields.append(player.salary)

            for ability, new_ability in zip(player.abilities, data.abilities):
                ability.current.value = new_ability.current
                ability.current_max.value = new_ability.current_max
                ability.max.value = new_ability.max

            for ability in player.abilities:
                bits_fields.append(ability.current)
                bits_fields.append(ability.current_max)
                bits_fields.append(ability.max)
            self._save(bits_fields)
        return True

    def save_other_team_friendly(self, team_index: int, friendly: int) -> bool:
        team = self.other_teams[team_index]
        team.friendly.value = friendly
        bits_fields = list()
        bits_fields.append(team.friendly)
        self._save(bits_fields)
        return True

    def save_town(self, data: TownDto) -> bool:
        self.town.living.value = data.living
        self.town.economy.value = data.economy
        self.town.sports.value = data.sports
        self.town.env.value = data.env
        self.town.population.value = data.population
        self.town.price.value = data.price
        self.town.traffic_level.value = data.traffic_level
        self.town.soccer_pop.value = data.soccer_pop
        self.town.soccer_level.value = data.soccer_level
        bits_fields = list()
        bits_fields.append(self.town.living)
        bits_fields.append(self.town.economy)
        bits_fields.append(self.town.sports)
        bits_fields.append(self.town.env)
        bits_fields.append(self.town.population)
        bits_fields.append(self.town.price)
        bits_fields.append(self.town.traffic_level)
        bits_fields.append(self.town.soccer_pop)
        bits_fields.append(self.town.soccer_level)
        self._save(bits_fields)
        return True

    def reset(self): ...

    def game_ver(self) -> int:
        return 1

    def _save(
        self,
        bit_fields: list[IntBitField | StrBitField],
        head_bytes: bytes = None,
    ):
        for bit_field in bit_fields:
            self.out_bit_stream.pack_bits(bit_field)
        self.entry_reader.update_decode_buffer(self.out_bit_stream.input_data)
        encode_buffer = self.entry_reader.enc()
        save_bin = self.entry_reader.build_save_bytes(encode_buffer)
        mc_reader = MemcardReader(self.path)
        mc_reader.write_save_entry(self.selected_game, save_bin, head_bytes)
