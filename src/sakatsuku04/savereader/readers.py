import struct
from typing import override

from ..constants import scout_excl_tbl, scout_simi_excl_tbl, team_ids
from ..data_reader import DataReader
from ..dtos import (
    AbroadDto,
    ClubDto,
    CoachDto,
    MyPlayerDto,
    MyTeamPlayerDto,
    OtherTeamPlayerDto,
    ScoutDto,
    SearchDto,
    SponsorDto,
    TownDto,
)
from ..io import CnVer, InputBitStream, IntBitField, OutputBitStream, StrBitField
from ..objs import Player, Reseter
from ..savereader.memcard_reader import MemcardReader
from ..utils import find_name_matches, get_album_bit_indices
from .entry_reader import EntryReader, HeadEntryReader
from .models import (
    Club,
    MyCoach,
    MyPlayer,
    MyPlayerAbility,
    MyScout,
    MySponsor,
    MyTeam,
    OtherPlayer,
    OtherTeam,
    Sche,
    Town,
)


class BaseReader:
    base_offset = 0x703D50

    def __init__(self, bit_stream: InputBitStream):
        self.bit_stream = bit_stream

    def print_mem_offset(self, start: int = 0):
        print(hex(self.bit_stream.unpacked_bytes_length + ClubReader.start + BaseReader.base_offset - start))


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
        club.year, club.month, club.date, club.day = self.bit_stream.unpack_bits([0xE, 4, 5, 3], 8)
        club.funds = self.bit_stream.unpack_bits(0x20)  # 0x8(4)
        club.manager_name = self.bit_stream.unpack_str(0x10)  # 00703D5C 0xC(16)
        manager_name2 = self.bit_stream.unpack_str(0x10)  # 0x1c(16)
        club.club_name = self.bit_stream.unpack_str(0x15)  # 0x2c(21)
        a = self.bit_stream.unpack_str(0x1CB)  #  - 00703F5B 0x41(459)
        b = a.byte_array
        club.version_magic = b[0:4]
        # 0x20c
        self.bit_stream.unpack_bits(3, 2)
        self.bit_stream.unpack_bits([0x10, 0x10], 6)
        self.bit_stream.unpack_bits(
            [0x20, 0xB, 1, 1, 1, 8, 8, 8, 8, 0xB, 0xB, 0xB, 0xB, 0xB, 0xB, 0xB, 0xB], 30
        )  # 0x703f82
        # 0x232
        self.bit_stream.unpack_bits([8, 8, 8, 8, 8, 8, 8, 8, 8, 4], 14)  # 0x703f90
        # 0x240
        self.bit_stream.unpack_bits([0x20] * 32)  # 0x704010
        # self.print_mem_offset(0x703D50)
        for _ in range(50):
            self.bit_stream.unpack_bits([0x10, 8, 8, 8], 8)
            self.bit_stream.unpack_bits([0x20] * 16)
        self.bit_stream.unpack_bits([0x20] * 48)
        for _ in range(114):
            self.bit_stream.unpack_bits([0x10, 8], 4)
        # 0x7050a8
        self.bit_stream.unpack_bits([0x10, 8, 8, 8, 8, 8, 8, 0x10, 8, 8, 8, 8, 8, 8, 0x10, 8, 8, 0x10, 0x10])
        # 0x7050c0
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10, 0x10], 12)
        # 0x7050cc
        club.seed = self.bit_stream.unpack_bits(0x20)  # 137c(4) seed_sim
        # 0x7050d0
        seed2 = self.bit_stream.unpack_bits(0x20)  # 1380(4) seed_game
        # 0x1384
        a = self.bit_stream.unpack_bits([8, 5, 0x10, 1], 8)
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
        # 0x2e
        team.english_name = self.bit_stream.unpack_str(0x20)
        self.bit_stream.unpack_bits([8] * 57)
        team.oilis_english_name = self.bit_stream.unpack_str(0x20)
        self.bit_stream.unpack_bits([8] * 15)
        self.bit_stream.unpack_bits([16, 16, 8, 8])  # 7051BF
        # 0x7051c0 0xbc
        team.players, team.master_coach = self.read_my_team_data()
        # 0x4698
        team.national_team_players, team.national_team_coach = self.read_my_team_data()  # 国家队
        # 0070DD78 0x8c74
        for _ in range(20):  # edit player, but not useful
            a = self.bit_stream.unpack_bits(0x10)
            a = self.bit_stream.unpack_str(0xD)
            # print(a.value)
            a = self.bit_stream.unpack_bits([8] * 0x15, 0x16)
            a = self.bit_stream.unpack_bits([8] * 0x2B)
            # print([hex(z.value) for z in a ])
            self.bit_stream.unpack_bits(0x10)
        # 0x92dc
        players = self._read_my_players(1)  # edit player
        #
        for _ in range(7):
            self.bit_stream.unpack_bits([-6, 8], 2)
            self.bit_stream.unpack_bits([8] * 10)
        #
        self.bit_stream.unpack_bits(8)
        #
        self.bit_stream.align(1)
        # 0x70e676 0x9572
        a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10], 10)
        team.team_status = a[0]  # 0x9572
        # 0x9574 0x9576 0x9578 team_pop
        # 0x70e680 0x957c
        for _ in range(0x19):
            a = self.bit_stream.unpack_bits([1] * 10, 10)  # player_work
        # 0x70e77a 0x9676
        for _ in range(0x19):
            a = self.bit_stream.unpack_bits([7] * 6, 6)  # pl_hexagon_set
        # 0x70e810
        a = self.bit_stream.unpack_bits([0x20] * 0x19)
        # 0x70e874 0x9770
        for _ in range(0x19 + 2):
            self.bit_stream.unpack_bits([8, 8], 2)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 7, 7, 7, 0xA], 9)
            self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 7, 7, 7, 0xA], 9)
            self.bit_stream.unpack_bits([2] * 48, 48)
        # 0x70efa0 0x9e9c
        self.bit_stream.unpack_bits([2, 8, 6], 4)
        # 0x70efa4 0x9ea0
        for _ in range(7):
            self.bit_stream.unpack_bits([1, 1, 0x10, 6], 6)
        # 0x70efce 0x9eca
        self.bit_stream.align(2)
        self.bit_stream.unpack_bits([0x20] * 2)
        # 0x70efd8 0x9ed4
        self.bit_stream.unpack_bits([8] * (0x2E + 9))
        # 0x70f00f 0x9f0b
        self.bit_stream.align(1)
        self.bit_stream.unpack_bits([1] * (3 + 0x2E + 21), 3 + 0x2E + 21)
        # 0x70f056 0x9f52
        self.bit_stream.unpack_bits([6], 2)
        self.bit_stream.unpack_bits([5, 5, 1, 1, 0x10], 7)
        # 0x70f05f 0x9f5b
        self.bit_stream.unpack_bits([8, 0x20], 5)
        # 0x70f064 0x9f60
        self.bit_stream.unpack_bits([8] * 0xF)
        # 0x70f073 0x9f6f
        self.bit_stream.unpack_bits([1] * (0x11 * 2 + 0xF), 0x11 * 2 + 0xF + 4)
        # 0x70f0a8 0x9fa4
        team.youth_players = self._read_my_players(0x18)
        # 0x7126a8 0xd5a4
        self.bit_stream.unpack_bits([-3, 3], 2)
        # 0x7126aa 0xd5a6
        for _ in range(0x18):
            self.bit_stream.unpack_bits([7] * 6, 6)
        # 0x71273a d636
        self.bit_stream.align(2)
        team.coach_candidates = []
        # 0x71273c d638 監督候補list
        for _ in range(0x12):
            coach_id, offer_years, age = self.bit_stream.unpack_bits([0x10, 3, 8], 4)
            if coach_id and coach_id.value != 0xFFFF:
                team.coach_candidates.append(MyCoach(id=coach_id, age=age, offer_years=offer_years))
        # 0x712784 d680 監督候補n人目のコーチlist
        for _ in range(0x16 * 3):
            self.bit_stream.unpack_bits([0x10, 3, 8], 4)
        # 0x71288c d788(156) 球探list
        team.my_scouts = []
        team.transfer_players = []
        for _ in range(3):
            self.bit_stream.unpack_bits(4, 2)  # index
            name = self.bit_stream.unpack_str(0xD)  # 2(d)
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
            # 0x1e
            abilities = self.bit_stream.unpack_bits([7] * 21, 21)
            # 0x7128bf 0x33
            a = self.bit_stream.unpack_bits([8, 8, 8, 0x10, 3, 3, 2], 9)
            un = a[0]  # 0x7128c0 0x33(1)
            area1 = a[1]  # 0x7128c1 0x34(1)
            area2 = a[2]  # 0x7128c2 0x35(1)
            id = a[3]  # 0x7128c3 0x36(2)
            task_type = a[6]  # 0x3a(2)
            # 0x7128c8 0xd7c4 转会球员list 0x3c
            for _ in range(5):
                a = self.bit_stream.unpack_bits([0x10, 0xB, 4, 6, 8], 8)
                tp_id = a[0]  # 0xd7c4(2)
                tp_age = a[3]  # 0xd7c9(1)
                if tp_id.value != 0xFFFF:
                    tp = OtherPlayer(id=tp_id, age=tp_age)
                    team.transfer_players.append(tp)
                self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
            self.bit_stream.unpack_bits([0xE, 4, 5, 3], 6)
            self.bit_stream.unpack_bits([8, 8, 4, 3, 0xB, 8, 0x10, 0xB, 0xB, 0xB, 0xB, 0xB], 20)
            my_scout = MyScout(id, age)
            my_scout.saved_name = name
            my_scout.abilities = abilities
            my_scout.area1 = area1
            my_scout.area2 = area2
            team.my_scouts.append(my_scout)
        # 0x712a60 0xd95c
        team.scout_candidates = []
        for _ in range(0xA):  # スカウト候補リスト
            scout_id, offer_years, age = self.bit_stream.unpack_bits([0x10, 3, 8], 4)
            if scout_id and scout_id.value != 0xFFFF:
                scout = MyScout(scout_id, age)
                team.scout_candidates.append(scout)
        # 0x712a88 0xd984
        team.my_coaches = []
        team.my_coaches.append(team.master_coach)
        for _ in range(4):  # coach
            self.bit_stream.unpack_bits(3, 2)  # index
            coach_name = self.bit_stream.unpack_str(0xD)  # 0x712a8a 0xd986
            # 0x712a97 0xd993
            a = self.bit_stream.unpack_bits([8, 4, 3, 8, 7, 0x10, 4, 4, 4, 4], 11)
            coach_age = a[1]  # 0x712a98 0xd994
            # 0x712aa2 0xd99e
            a = self.bit_stream.unpack_bits([7, 7, 7, 1, 0x10, 3, 3, 3, 3, 2, 3, 4, 8, 4, 4, 3, 2], 18)
            self.bit_stream.unpack_bits([7] * 0x35, 0x35)
            # 0x712ae9 0xd9e5
            a = self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 14)
            coach_id = a[9]  # 0xd9ee(2)
            self.bit_stream.unpack_bits([0x10] * 9, 20)
            self.bit_stream.unpack_bits(1, 1)
            # 0x712b0c 0xda08
            if coach_id.value != 0xFFFF:
                team.my_coaches.append(MyCoach(id=coach_id, age=coach_age, saved_name=coach_name))
        # 0x712c98 0xdb94
        for _ in range(50):
            self.bit_stream.unpack_bits([9, 6, 6, 9, 3], 8)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x20, 0x10, 0x10, 0x10, 0x10])
            self.bit_stream.unpack_bits([0x15], 4)
            self.bit_stream.unpack_bits([0x15], 4)
            self.bit_stream.unpack_bits([0x20] * 13)
        # 0x713d00 0xebfc
        for _ in range(50):
            self.bit_stream.unpack_bits([8, 6, 8, 2], 4)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x20, 8], 12)
            self.bit_stream.unpack_bits([0x20] * 0x10)
            self.bit_stream.unpack_bits([8] * 0x10)
        # 0x714fc0 0xfebc
        for _ in range(8):
            self.bit_stream.unpack_bits([8] * 12)
        # 0x715020
        self.bit_stream.unpack_bits(1, 2)
        self.bit_stream.unpack_bits(4, 2)
        self.bit_stream.unpack_bits([0x10, 8, 8, 8, 1, 1, 1, 1, 1], 12)
        # 0x715030
        self.bit_stream.unpack_bits([0x20] * 0x10)
        team.my_sponsors = []
        # 0x715070 0xff6c 赞助商
        for _ in range(7):
            a = self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 3, 0x10, 1, 1], 10)
            id = a[0]
            if id.value == 0 or id.value == 0xFF:
                continue
            contract_years = a[1]
            offer_years = a[2]
            amount = a[6]
            team.my_sponsors.append(
                MySponsor(id=id, contract_years=contract_years, offer_years=offer_years, amount=amount)
            )
        # 0x7150b6
        self.bit_stream.unpack_bits([8] * 32)
        # 0xffd2
        self.bit_stream.unpack_bits([8] * 26)
        # 0xffec
        # 0x7150f0
        self.bit_stream.unpack_bits([0x20] * 3)
        self.bit_stream.unpack_bits(2, 2)
        # 0xfffa
        self.bit_stream.unpack_bits(0x10)
        # 0xfffc supporter_comp
        self.bit_stream.unpack_bits([0x10] * 10)
        # 0x10010
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
            for _ in range(168 * 2):
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
        # 0x260d4 图鉴球员
        team.album_players = self.bit_stream.unpack_bits([0x20] * 9)
        # 0x72b1fc 0x260f8 纪念相册
        for _ in range(26):
            un = self.bit_stream.unpack_str(0xD)
            self.bit_stream.unpack_bits([8, 4, 8, 8, 3, 4, 6, 3], 8)
            self.bit_stream.unpack_bits([8] * 18)
            self.bit_stream.unpack_bits([8] * (0x15 + 0x2B))
            self.bit_stream.unpack_bits([8, -6, 0x10], 5)
        # 0x72bcf4 0x26bf0 自由球员
        team.free_players = []
        for _ in range(16):
            a = self.bit_stream.unpack_bits([0x10, 0xB], 4)
            fp_id = a[0]  # 0x26bf0
            a = self.bit_stream.unpack_bits([4, 6, 8], 4)
            fp_age = a[1]  # 0x26bf5
            if fp_id.value != 0xFFFF:
                team.free_players.append(OtherPlayer(id=fp_id, age=fp_age))
            self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
        # 0x72bdd4 0x26cd0 新人球员
        team.rookie_players = []
        for _ in range(36):
            a = self.bit_stream.unpack_bits([0x10, 0xB], 4)
            rk_id = a[0]  # 0x26cd0
            a = self.bit_stream.unpack_bits([4, 6, 8], 4)
            rk_age = a[1]  # 0x26cd5
            if rk_id.value != 0xFFFF:
                team.rookie_players.append(OtherPlayer(id=rk_id, age=rk_age))
            a = self.bit_stream.unpack_bits([0x10, 0x10, 3, 8], 6)
        # 0x72bfcc 0x26ec8
        for _ in range(240):
            self.bit_stream.unpack_bits([0x10, 8], 4)
        # 0x72c38c 0x27288
        for _ in range(26):
            self.bit_stream.unpack_bits([8], 2)
            self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10])
        # 0x72c490 0x2738c
        self.bit_stream.unpack_bits([0x10] * 200)
        # 0x72c620 0x2751c tenshoku_scout_work 転職
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
        # 0x72c758 0x27654
        a = self.bit_stream.unpack_bits([0x10, 0x10, 8], 6)  # a[0]: mr_work
        self.bit_stream.unpack_bits(0x10)
        # 0x72c760
        for _ in range(12):
            a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10], 8)
        # 0x276ac
        self.bit_stream.unpack_bits([0x20, 0x20, 0x20])
        # 0x276b8
        self.bit_stream.unpack_bits([0x10, 0x10, 0x10])  # rental_player_work
        # 0x276be
        self.bit_stream.unpack_bits([3, 3], 2)
        # 0x276c0
        self.bit_stream.unpack_bits([0x10] * 2)
        fail_player_id = a[1]  # 0x276c2
        # 0x276c4
        self.bit_stream.unpack_bits([0x20] * 6)
        # 0x72c7e0 0x276dc
        self.bit_stream.padding(self.tail_padding)
        # 0x72c7f0
        return team

    def _read_my_players(self, count: int) -> list[MyPlayer]:
        players: list[MyPlayer] = [MyPlayer(i) for i in range(count)]
        # each player produce 0x240 bytes
        # 0x7051E0
        for i in range(count):
            players[i].id, players[i].pos, players[i].age = self.bit_stream.unpack_bits([0x10, 4, 7], 4)  # 7051E4
            for ll in range(0x40):
                current, current_max, max = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
                players[i].abilities.append(MyPlayerAbility(ll, current, current_max, max))  # 705364
            from_team_id = self.bit_stream.unpack_bits(0xB)  # 184(2)
            players[i].name = self.bit_stream.unpack_str(0xD)  # 705364 186(13)
            a = self.bit_stream.unpack_bits([8, 8, 4, 4, 7, 8, 4, 7, 3, 7], 11)  # 70537E
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
            un = a[4]  # 0x705386 1a6
            # 70538C
            a = self.bit_stream.unpack_bits([7, 7, 7, 7, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], 16)
            players[i].desire = a[0]  # 0x70538C 1ac
            players[i].pride = a[1]  # 0x70538D 1ad
            players[i].ambition = a[2]  # 0x70538E 1ae
            players[i].persistence = a[3]  # 0x70538F 1af
            un = a[4]  # 0x705390
            players[i].tone_type = a[5]  # 0x705391 1b1
            un = a[6]  # 0x705392
            un = a[7]  # 0x705393
            un = a[8]  # 0x705394
            un = a[9]  # 0x705395
            un = a[10]  # 0x705396
            un = a[11]  # 0x705397 1b7
            players[i].patient = a[12]  # 0x705398 1b8
            un = a[13]  # 00705399
            players[i].cooperation_type = a[14]  # 0x70539A 1ba
            players[i].wave_type = a[15]  # 0x70539B 1bb
            # 70539C
            players[i].grow_type_phy = self.bit_stream.unpack_bits(4, 1)  # 0x70539C 1bc
            players[i].grow_type_tec = self.bit_stream.unpack_bits(4, 1)  # 0x70539D 1bd
            players[i].grow_type_sys = self.bit_stream.unpack_bits(4, 1)  # 0x70539E 1be
            a = self.bit_stream.unpack_bits([7, 4, 7, 3, 3, 7], 6)
            players[i].super_sub = a[0]  # 0x70539f 1bf
            players[i].wild_type = a[2]  # 0x7053a1 1c1
            players[i].weak_type = a[3]  # 0x7053a2 1c2
            players[i].tired_type = a[4]  # 0x7053a3 1c3
            base_pop = a[5]  # 0x7053a4 1c4
            players[i].style = self.bit_stream.unpack_bits(5, 1)  # 0x7053a5 1c5
            a = self.bit_stream.unpack_bits([1, 3, 4], 6)
            style_lock = a[0]  # 1c6
            # 0x7053ac
            a = self.bit_stream.unpack_bits([0x20, 2], 6)
            players[i].magic_value = a[0]  # 0x7053ac 1cc(4)
            # 0x7053B2
            a = self.bit_stream.unpack_bits([0xA, 8, 8, 0x10], 6)
            season_score = a[0]  # 0x7053B2 1d2(2)
            players[i].salary = a[3]  # 0x7053B6 1d6(2)
            # 7053B8
            a = self.bit_stream.unpack_bits([8, 3, 3, 8, 8, 8], 6)
            joined_years = a[0]  # 0x7053B8 1d8(1)
            players[i].offer_years_passed = a[1]  # 0x7053B9 1d9(1)
            players[i].offer_years_total = a[2]  # 0x7053B9A 1da(1)
            contract_cond = a[3]  # 0x7053B9B 1db(1)
            # 0x7053be
            a = self.bit_stream.unpack_bits([0x10] * 13, 26)
            players[i].comp_money = a[0]  # 0x7053be 1de(2) 待遇不满
            players[i].comp_discord = a[1]  # 0x7053c0 1e0(2) 人际关系不满
            players[i].comp_staff = a[2]  # 0x7053c2 1e2(2) 教练组不满
            players[i].comp_usage = a[3]  # 0x7053c4 1e4(2) 启用不满
            players[i].comp_result = a[4]  # 0x7053c6 1e6(2) 球队成绩不满
            players[i].comp_status = a[5]  # 0x7053c8 1e8(2) 球队声望不满
            players[i].comp_euipment = a[6]  # 0x7053ca 1ea(2) 设施不满
            players[i].pop = a[7]  # 0x7053cc 1ec(2) 人气
            pop_local = a[8]  # 0x7053ce 1ee(2) 本地人气
            pop_oversea = a[9]  # 0x7053d0 1f0(2) 海外人气
            players[i].tired = a[10]  # 0x7053D2 1f2(2)
            players[i].status = a[11]  # 0x7053D4 1f4(2)
            players[i].condition = a[12]  # 0x7053D6 1f6(2)
            players[i].moti = self.bit_stream.unpack_bits(0x10, 4)  # 1f8(4)
            # 7053DC
            a = self.bit_stream.unpack_bits([0x20, 0x10, 0x10, 0x10])  # 1fc(4) 200(2) 202(2) 204(2)
            players[i].power = a[3]  # 0x7053e4 204(2) 气力，max=1000
            # 0x7053e6
            a = self.bit_stream.unpack_bits([0x10, 0x10, 4, 7, 4, 7, 6, 4, 8, 4], 12)
            players[i].kan = a[0]  # 0x7053e6 206(2) 試合勘 比赛感觉
            players[i].return_days = a[1]  # 0x7053e8 208(2)
            injury_kind = a[2]  # 0x7053ea 20a(1)
            players[i].abroad_times = a[9]  # 0x7053f1 211(1)
            # 0x7053f2
            a = self.bit_stream.unpack_bits([0x10, 0x10, 7])
            captain_exp = a[0]  # 0x7053f2 212(2)
            keyman_exp = a[1]  # 0x7053f4 214(2)
            a = self.bit_stream.unpack_bits([-8] * 9, 9)  # not use
            # 0x705400
            a = self.bit_stream.unpack_bits([0x10, 0x10, 8, -8, 5, 5, 6], 12)
            a[0]  # 0x705400 220(2) mr_number
            players[i].explosion_exp = a[1]  # 0x705402 222(2) explosion_exp
            players[i].explosion_level = a[2]  # 0x705404 224(1) explosion_level
            players[i].explo_countdown = a[3]  # 0x705405 225(1) explo_countdown
            players[i].explo_pending_reason = a[4]  # 0x705406 226(1) explo_pending_reason
            players[i].explo_final_reason = a[5]  # 0x705407 227(1) explo_final_reason
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

    def read_my_team_data(self) -> tuple[list[MyPlayer], MyCoach]:
        # 0x7051c0 size: 0x45dc
        a = self.bit_stream.unpack_bits([16, 16, 1], 5)
        town_id = a[1]  # 0x7051c2 0x2(2)
        a = self.bit_stream.unpack_bits([-6] * 0x19, 0x19)  # pos_idx 场上位置
        self.bit_stream.align(2)
        # 0x7051e0 0x20
        players = self._read_my_players(0x19)
        # 0x3860
        self.bit_stream.unpack_bits(0x10)
        # 0x3862
        for _ in range(10):
            self.bit_stream.unpack_bits([-6], 2)
            self.bit_stream.unpack_bits(0x10)  # 708A4A
        # 0x388a
        self.bit_stream.unpack_bits([-6, -6, 5, -6, -6, -6, -6, -6, 2], 9)
        captain = a[1]  # 0x388b
        # 0x3893
        self.bit_stream.unpack_bits([5, 3, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3] * 3, 60)
        self.bit_stream.align(1)
        # 0x708a90 0x38d0
        for _ in range(0x19):  # team_combi
            a = self.bit_stream.unpack_bits([0x10] * 0x19)
        # 0x708f72 0x3db2
        self.bit_stream.unpack_bits([8] * 3)
        a = self.bit_stream.unpack_bits([8] * 0x19)
        # 0x3dce
        self.bit_stream.unpack_bits(3, 2)
        # 0x3dd0
        coach_name = self.bit_stream.unpack_str(0xD)  # coach name
        # 0x3dd0
        a = self.bit_stream.unpack_bits([8, 4, 3, 8, 7, 0x10, 4, 4, 4, 4, 7, 7, 7, 1], 15)
        coach_born = a[0]  # 0x3dd0
        coach_age = a[3]  # 0x3dd3
        # 0x3dec
        a = self.bit_stream.unpack_bits([-0x10, 3, 3, 3, 3, 2, 3, 4, 8, 4, 4, 3, 2], 14)
        # 708FBA 0x3dfa
        a = self.bit_stream.unpack_bits([7] * 0x35, 0x35)
        # 0x3e2f
        a = self.bit_stream.unpack_bits([8, 8, 5, 5, 5, 5, 5, 5, 3, 0x10, 3, 3, 3], 15)
        coach_id = a[9]  # 0x3e38(2)
        self.bit_stream.unpack_bits([0x10] * 9)
        self.bit_stream.unpack_bits(1, 2)
        # 0x3e52
        self.bit_stream.unpack_bits([3, 1], 2)
        # 0x3e54
        for _ in range(12):
            self.bit_stream.unpack_bits([8, 8, 1, 1], 4)
            self.bit_stream.unpack_bits([1] * 0x19, 0x19)
            self.bit_stream.unpack_bits([8, 5, 5, 8, 3] * 12, 5 * 12)
        for _ in range(0x19):
            self.bit_stream.unpack_bits([8, 3] * 12, 2 * 12)
        for _ in range(7):
            self.bit_stream.unpack_bits(8)
            for _ in range(3):
                self.bit_stream.unpack_bits([-6, 8], 2)
                self.bit_stream.unpack_bits([8] * 0xA)
        self.bit_stream.unpack_bits(8)
        master_coach = MyCoach(id=coach_id, age=coach_age, saved_name=coach_name)
        return players, master_coach


class OtherTeamReader(BaseReader):
    start = TeamReader.start + TeamReader.size  # 0x72c7f0
    size = 0x89C0
    total_size = TeamReader.total_size + size
    consume_bytes = 0x208B5
    consume_bits = 0x1045A2
    remain_mask = 0x20
    tail_padding = b"\x40\x03\xbf\xfc" * 4

    def read(self) -> list[OtherTeam]:
        teams: list[OtherTeam] = []
        for i in range(0x109):  # loop the teams
            id = self.bit_stream.unpack_bits(0x10)
            players: list[OtherPlayer] = []
            for _ in range(0x19):  # loop the playes
                pid, age, ability_graph = self.bit_stream.unpack_bits([0x10, 7, 8], 4)
                player = OtherPlayer(pid, age, ability_graph)
                players.append(player)
            unknown1, unknown2, friendly = self.bit_stream.unpack_bits([0x10, 0x10, 7], 6)  # 72c856 - 72c85b
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
        self.bit_stream.unpack_bits(3, 2)  # 0, 1
        a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10, 0x10], 10)
        town.living = a[0]  # 2(2)
        town.economy = a[1]  # 4(2)
        town.sports = a[2]  # 6(2)
        town.env = a[3]  # 8(2)
        # 0xb
        town.population = self.bit_stream.unpack_bits(0x20)  # 0xc(4)
        # 0xf
        a = self.bit_stream.unpack_bits([7, 7, 7, 8, 8], 8)
        town.price = a[0]  # 0x10
        town.traffic_level = a[1]  # 0x11
        town.soccer_pop = a[2]  # 0x12
        # 0x18
        a = self.bit_stream.unpack_bits([0x10, 0x10, 0x10])
        town.soccer_level = a[2]  # 0x1c(2)
        # 0x1e
        for _ in range(3):  # 姐妹都市
            self.bit_stream.unpack_bits([0x10, 0xE], 4)
            self.bit_stream.unpack_bits([4, 5, 3, 8], 6)
        # 0x73552c 0x3c
        a = self.bit_stream.unpack_bits([3, 4, 8], 3)
        weather = a[0]  # 0x3c
        town.town_type = a[1]  # 0x3d
        # 0x3f
        self.bit_stream.unpack_bits([1] * 13, 13)
        # 0x4c
        self.bit_stream.unpack_bits([1] * 39, 39)
        # 0x73
        self.bit_stream.unpack_bits([1] * 39, 39)
        # 0x9a promote_list 地域振興案
        self.bit_stream.unpack_bits([1] * 39, 39)
        # 0xc1
        self.bit_stream.unpack_bits([4] * 13, 13)
        # 0xce
        self.bit_stream.unpack_bits([2] * 39, 39)
        # 0xf5
        self.bit_stream.unpack_bits([2] * 39, 39)
        # 0x11c
        self.bit_stream.unpack_bits([2] * 39, 39)
        # 0x143
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

    def read(self) -> Sche:
        sche = Sche()
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
            self.bit_stream.unpack_bits(0xB, 2)
            self.bit_stream.unpack_bits(0xB, 2)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(8, 1)
            self.bit_stream.unpack_bits(0x10)
        # 0x764128 0x7ac
        for _ in range(4):
            self.bit_stream.unpack_bits(0xE, 2)
            self.bit_stream.unpack_bits(0x4, 1)
            self.bit_stream.unpack_bits(0x5, 1)
            self.bit_stream.unpack_bits(0x3, 2)
            self.bit_stream.unpack_bits(0x10)
            self.bit_stream.unpack_bits(0x5, 2)
            self.bit_stream.unpack_bits(0xB, 2)
            self.bit_stream.unpack_bits(0xB, 2)
            self.bit_stream.unpack_bits(0xB, 2)
        # 0x764168 0x7ec
        for _ in range(64):
            self.bit_stream.unpack_bits(0x1, 1)
        # 0x7641a8 0x82c
        for _ in range(32):
            self.bit_stream.unpack_bits(0x1, 1)
        # 0x7641c8 0x84c # 留学地list
        sche.abroad_list = []
        for _ in range(70):
            a = self.bit_stream.unpack_bits(0x2, 2)
            b = self.bit_stream.unpack_bits(0x10)
            sche.abroad_list.append(a)
            # print(f"({a.value}, {b.value}),")
        # print("===========")
        # 0x7642e0 0x964 # 集训地list
        sche.camp_list = []
        for _ in range(40):
            a = self.bit_stream.unpack_bits(0x2, 2)
            b = self.bit_stream.unpack_bits(0x10)
            sche.camp_list.append(a)
            # print(a.value, b.value)
        # self.print_mem_offset(0x76397c)
        # 0x764380 0xa04
        self.bit_stream.padding(self.tail_padding)
        return sche


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
        self.entry_reader: EntryReader
        self.out_bit_stream: OutputBitStream
        self.selected_game: str
        self.club: Club
        self.my_team: MyTeam
        self.other_teams: list[OtherTeam]
        self.town: Town
        self.sche: Sche

    @override
    def games(self) -> list[str]:
        return list(self.save_entries.keys())

    @override
    def select_game(self, game: str) -> int:
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
        self.sche = sche_reader.read()
        game_ver = self.game_ver()
        CnVer.set_ver(game_ver)
        Reseter.reset()
        return game_ver

    @override
    def read_club(self) -> ClubDto:
        if not self.selected_game:
            return None
        club_dto = self.club.to_dto()
        club_dto.team_status = self.my_team.team_status.value
        return club_dto

    def _read_team_players(self, players) -> list[MyTeamPlayerDto]:
        valid_players = filter(lambda p: p.id.value != 0xFFFF, players)
        sorted_players = sorted(valid_players, key=lambda p: p.pos.value)
        return [MyTeamPlayerDto(id=p.id.value, name=p.name.value, pos=p.pos.value) for p in sorted_players]

    @override
    def read_myteam(self) -> list[MyTeamPlayerDto]:
        return self._read_team_players(self.my_team.players)

    @override
    def read_youth_team(self) -> list[MyTeamPlayerDto]:
        return self._read_team_players(self.my_team.youth_players)

    @override
    def read_national_team(self) -> list[MyTeamPlayerDto]:
        return self._read_team_players(self.my_team.national_team_players)

    @override
    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        team = self.other_teams[team_index]
        result = []
        for player in [player for player in team.players if player.id.value != 0xFFFF]:
            result.append(player.to_dto())
        return sorted(result, key=lambda player: player.pos)

    @override
    def read_other_team_friendly(self, team_index: int) -> int:
        team = self.other_teams[team_index]
        return team.friendly.value

    @override
    def read_myplayer(self, id: int, team: int) -> MyPlayerDto:
        if team == 0:
            player = list(filter(lambda p: p.id.value == id, self.my_team.players)).pop()
        elif team == 1:
            player = list(filter(lambda p: p.id.value == id, self.my_team.youth_players)).pop()
        else:
            player = list(filter(lambda p: p.id.value == id, self.my_team.national_team_players)).pop()
        return player.to_dto()

    @override
    def search_player(self, data: SearchDto) -> list[OtherTeamPlayerDto]:
        name = data.name
        pos = data.pos
        age = data.age
        country = data.country
        tone = data.tone
        cooperation = data.cooperation
        rank = data.rank
        style = data.style
        scout_action = data.scout_action
        ids = []
        match scout_action:
            case None | 0:
                for team in self.other_teams:
                    for player in team.players:
                        if player.id.value != 0xFFFF:
                            if age and age != player.age.value:
                                continue
                            ids.append(player.id.value)
            case 1:
                for p in self.my_team.transfer_players:
                    ids.append(p.id.value)
            case 2:
                for p in self.my_team.free_players:
                    ids.append(p.id.value)
            case 3:
                for p in self.my_team.rookie_players:
                    ids.append(p.id.value)
            case _:
                return []
        filter_players = {k: v for k, v in Player.player_dict().items() if k in ids}
        filter_ids = find_name_matches(filter_players, name) if name else ids
        result = []

        def _match_filters(dto: OtherTeamPlayerDto) -> bool:
            if pos is not None and pos != dto.pos:
                return False
            if country is not None and ((country == 50 and dto.born > 50) or (country != 50 and dto.born != country)):
                return False
            if style is not None and style != dto.style:
                return False
            if tone is not None and tone != dto.tone_type:
                return False
            if cooperation is not None and cooperation != dto.cooperation_type:
                return False
            return not (rank is not None and rank != dto.rank)

        if not scout_action:
            for i, team in enumerate(self.other_teams):
                for player in team.players:
                    if player.id.value in filter_ids:
                        dto = player.to_dto()
                        if _match_filters(dto):
                            dto.team_index = i
                            result.append(dto)
        else:
            if scout_action == 1:
                filter_players = [f for f in self.my_team.transfer_players if f.id.value in filter_ids]
            elif scout_action == 2:
                filter_players = [f for f in self.my_team.free_players if f.id.value in filter_ids]
            else:
                filter_players = [f for f in self.my_team.rookie_players if f.id.value in filter_ids]
            for p in filter_players:
                dto = p.to_dto()
                if _match_filters(dto):
                    dto.team_index = -1
                    result.append(dto)
        return sorted(result, key=lambda player: player.pos)

    @override
    def read_town(self) -> TownDto:
        return self.town.to_dto()

    @override
    def read_my_album_players(self) -> list[int]:
        players_raw = [p.value for p in self.my_team.album_players]
        byte_data = bytearray()
        for val in players_raw:
            byte_data.extend(struct.pack("<I", val))
        return get_album_bit_indices(byte_data)

    @override
    def read_scouts(self, type: int) -> list[ScoutDto]:
        scouts = (
            [f.to_dto() for f in self.my_team.my_scouts]
            if type == 0
            else [f.to_dto_with_name(f.id.value) for f in self.my_team.scout_candidates]
        )

        if not scouts:
            return []

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

    @override
    def read_coaches(self, type: int) -> list[CoachDto]:
        coaches = (
            [f.to_dto() for f in self.my_team.my_coaches]
            if type == 0
            else [f.to_dto_with_name(f.id.value) for f in self.my_team.coach_candidates]
        )

        if not coaches:
            return []

        return coaches

    @override
    def read_my_abroads(self, type: int) -> list[AbroadDto]:
        dtos = AbroadDto.get_abr_camp_teams(type)
        for i, dto in enumerate(dtos):
            dto.is_enabled = self.sche.abroad_list[i].value != 0 if type == 0 else self.sche.camp_list[i].value != 0
        return dtos

    @override
    def read_one_abroad(self, index: int, type: int) -> AbroadDto:
        return AbroadDto.get_abr_camp_dto(index, type)

    @override
    def save_club(self, club_data: ClubDto) -> bool:
        save_entry = self.save_entries.get(self.selected_game)
        if not save_entry:
            return False
        self.club.funds.value = club_data.combo_funds()
        self.club.year.value = club_data.year + 2003
        self.club.difficulty.value = club_data.difficulty
        bits_fields = []
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

    @override
    def save_player(self, data: MyPlayerDto, team: int) -> bool:
        player = (
            list(filter(lambda p: p.id.value == data.id, self.my_team.players)).pop()
            if team == 0
            else list(filter(lambda p: p.id.value == data.id, self.my_team.youth_players)).pop()
        )
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
            player.offer_years_passed.value = min(data.offer_years_passed, data.offer_years_total)
            player.offer_years_total.value = data.offer_years_total
            player.comp_money.value = data.comp[0]
            player.comp_discord.value = data.comp[1]
            player.comp_staff.value = data.comp[2]
            player.comp_usage.value = data.comp[3]
            player.comp_result.value = data.comp[4]
            player.comp_status.value = data.comp[5]
            player.comp_euipment.value = data.comp[6]
            bits_fields = []
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
            bits_fields.append(player.offer_years_passed)
            bits_fields.append(player.offer_years_total)
            bits_fields.append(player.comp_money)
            bits_fields.append(player.comp_discord)
            bits_fields.append(player.comp_staff)
            bits_fields.append(player.comp_usage)
            bits_fields.append(player.comp_result)
            bits_fields.append(player.comp_status)
            bits_fields.append(player.comp_euipment)

            for ability, new_ability in zip(player.abilities, data.abilities, strict=False):
                ability.current.value = new_ability.current
                ability.current_max.value = new_ability.current_max
                ability.max.value = new_ability.max

            for ability in player.abilities:
                bits_fields.append(ability.current)
                bits_fields.append(ability.current_max)
                bits_fields.append(ability.max)
            self._save(bits_fields)
        return True

    @override
    def save_other_team_friendly(self, team_index: int, friendly: int) -> bool:
        team = self.other_teams[team_index]
        team.friendly.value = friendly
        bits_fields = []
        bits_fields.append(team.friendly)
        self._save(bits_fields)
        return True

    @override
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
        bits_fields = []
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

    @override
    def read_sponsors(self, type: int) -> list[SponsorDto]:
        sponsors: list[SponsorDto] = [f.to_dto() for f in self.my_team.my_sponsors] if type == 0 else []
        if not sponsors:
            return []
        my_abroads = [f.id for f in self.read_my_abroads(0) if f.is_enabled]
        my_camps = [f.id for f in self.read_my_abroads(1) if f.is_enabled]
        for sponsor in sponsors:
            sponsor.enabled_abr_ids = my_abroads
            sponsor.enabled_camp_ids = my_camps
        return sponsors

    @override
    def reset(self): ...

    @override
    def game_ver(self) -> int:
        if self.club.version_magic == b"\x83\xaf\x8e\xd7":
            return 1
        if self.club.version_magic == b"\x83\xaf\x8e\xd6":
            return 2
        return 0

    def _save(
        self,
        bit_fields: list[IntBitField | StrBitField],
        head_bytes: bytes | None = None,
    ):
        for bit_field in bit_fields:
            self.out_bit_stream.pack_bits(bit_field)
        self.entry_reader.update_decode_buffer(self.out_bit_stream.input_data)
        encode_buffer = self.entry_reader.enc()
        save_bin = self.entry_reader.build_save_bytes(encode_buffer)
        mc_reader = MemcardReader(self.path)
        mc_reader.write_save_entry(self.selected_game, save_bin, head_bytes)
