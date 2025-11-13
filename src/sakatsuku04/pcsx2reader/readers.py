import ctypes
import importlib.resources
import platform
import struct
from ctypes import c_bool, c_char, c_char_p, c_uint, c_ulong, c_void_p
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
from ..io import CnVer, IntByteField, StrByteField
from ..objs import Player, Reseter
from ..utils import find_name_matches, get_album_bit_indices
from .models import Club, MyCoach, MyPlayer, MyPlayerAbility, MyScout, OtherPlayer, OtherTeam, Town


class Pcsx2DataReader(DataReader):
    def __init__(self):
        # we get the correct library extension per os
        lib = "libpine_c"
        cur_os = platform.system()
        if cur_os == "Linux":
            lib = "libpine_c.so"
        elif cur_os == "Windows":
            lib = "pine_c.dll"
        elif cur_os == "Darwin":
            lib = "libpine_c.dylib"
        with importlib.resources.path("sakatsuku04.libs", lib) as file_path:
            self.libipc = ctypes.CDLL(file_path)
        self.libipc.pine_pcsx2_new.restype = c_void_p
        self.libipc.pine_read.argtypes = [c_void_p, c_uint, c_char, c_bool]
        self.libipc.pine_read.restype = c_ulong
        self.libipc.pine_get_error.argtypes = [c_void_p]
        self.libipc.pine_get_error.restype = c_uint
        self.libipc.pine_pcsx2_delete.argtypes = [c_void_p]
        self.libipc.pine_pcsx2_delete.restype = None
        self.libipc.pine_write.argtypes = [c_void_p, c_uint, c_ulong, c_char, c_bool]
        self.libipc.pine_write.restype = None
        self.libipc.pine_status.argtypes = [c_void_p, c_bool]
        self.libipc.pine_status.restype = c_uint
        self.libipc.pine_getgametitle.argtypes = [c_void_p, c_bool]
        self.libipc.pine_getgametitle.restype = c_char_p
        self.libipc.pine_getgameid.argtypes = [c_void_p, c_bool]
        self.libipc.pine_getgameid.restype = c_char_p
        self.libipc.pine_getgameuuid.argtypes = [c_void_p, c_bool]
        self.libipc.pine_getgameuuid.restype = c_char_p
        self.libipc.pine_getgameversion.argtypes = [c_void_p, c_bool]
        self.libipc.pine_getgameversion.restype = c_char_p
        self.ipc = self.libipc.pine_pcsx2_new()
        self.destroyed = False
        self._read_funcs = {
            1: self._read_8bit,
            2: self._read_16bit,
            4: self._read_32bit,
            8: self._read_64bit,
        }
        self._write_funcs = {
            1: self._write_8bit,
            2: self._write_16bit,
            4: self._write_32bit,
            8: self._write_64bit,
        }

    def _read_8bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(0), False)

    def _read_16bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(1), False)

    def _read_32bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(2), False)

    def _read_64bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(3), False)

    def _read_str(self, address: int, length: int) -> bytes:
        result = bytearray()
        for i in range(length):
            int_value = self._read_8bit(address + i)
            result += int_value.to_bytes(1, "little")
        return bytes(result)

    def _write_8bit(self, address: int, value: int):
        self.libipc.pine_write(self.ipc, address, c_ulong(value), c_char(4), False)

    def _write_16bit(self, address: int, value: int):
        self.libipc.pine_write(self.ipc, address, c_ulong(value), c_char(5), False)

    def _write_32bit(self, address: int, value: int):
        self.libipc.pine_write(self.ipc, address, c_ulong(value), c_char(6), False)

    def _write_64bit(self, address: int, value: int):
        self.libipc.pine_write(self.ipc, address, c_ulong(value), c_char(7), False)

    def _write_str(self, address: int, value: bytes):
        for i in range(len(value)):
            self._write_8bit(address + i, value[i])

    def _get_error(self) -> int:
        return self.libipc.pine_get_error(self.ipc)

    def _get_emu_status(self) -> int:
        return self.libipc.pine_status(self.ipc, False)

    def _read_int_byte(self, address: int, byte_length: int = 1) -> IntByteField:
        if byte_length not in self._read_funcs:
            raise ValueError(f"Unsupported byte length: {byte_length}")
        value = self._read_funcs[byte_length](address)
        return IntByteField(byte_length, value, address)

    def _write_int_byte(self, byte_field: IntByteField):
        self._write_funcs[byte_field.byte_length](byte_field.byte_offset, byte_field.value)

    def _read_str_byte(self, address: int, byte_length: int = 1) -> StrByteField:
        value = self._read_str(address, byte_length)
        return StrByteField(value, address)

    def _write_str_byte(self, byte_field: StrByteField):
        self._write_str(byte_field.byte_offset, byte_field.byte_array)

    def _read_club(self) -> Club:
        club = Club()
        club.year = self._read_int_byte(0x703D50, 2)
        club.month = self._read_int_byte(0x703D52)
        club.date = self._read_int_byte(0x703D53)
        club.day = self._read_int_byte(0x703D54)
        club.funds = self._read_int_byte(0x703D58, 4)
        club.difficulty = self._read_int_byte(0x7050D5)
        club.manager_name = self._read_str_byte(0x703D5C, 0x10)
        club.club_name = self._read_str_byte(0x703D7C, 0x15)
        club.seed = self._read_int_byte(0x7050CC, 4)
        club.team_status = self._read_int_byte(0x70E676, 2)
        return club

    def _read_myteam(self) -> list[MyPlayer]:
        my_players = []
        for i in range(0x19):
            player = MyPlayer()
            player.index = i
            player.id = self._read_int_byte(0x7051E0 + i * 0x240, 2)
            player.pos = self._read_int_byte(0x7051E2 + i * 0x240)
            player.name = self._read_str_byte(0x705366 + i * 0x240, 0xD)
            my_players.append(player)
        return my_players

    def _read_youth_team(self) -> list[MyPlayer]:
        my_players = []
        for i in range(0x18):
            player = MyPlayer()
            player.index = i
            player.id = self._read_int_byte(0x70F0A8 + i * 0x240, 2)
            player.pos = self._read_int_byte(0x70F0AA + i * 0x240)
            player.name = self._read_str_byte(0x70F22E + i * 0x240, 0xD)
            my_players.append(player)
        return my_players

    def _read_other_teams(self) -> list[OtherTeam]:
        other_teams: list[OtherTeam] = []
        for i, id in enumerate(team_ids):
            id_field = IntByteField(2, id, 0)
            friendly_field = IntByteField(2, 0, 0)
            other_teams.append(OtherTeam(i, id_field, friendly_field))
        return other_teams

    def _read_other_team_players(self, team_index: int) -> list[OtherPlayer]:
        players = []
        for i in range(0x19):
            pid = self._read_int_byte(0x72C7F2 + team_index * 0x6C + i * 4, 2)
            age = self._read_int_byte(0x72C7F4 + team_index * 0x6C + i * 4)
            # number = self._read_int_byte(0x7337BC + team_index * 0x19 + i)
            player = OtherPlayer(pid, age)
            players.append(player)
        return players

    def _read_other_team_friendly(self, team_index: int) -> IntByteField:
        return self._read_int_byte(0x72C85A + team_index * 0x6C, 2)

    def _read_myplayer(self, id: int, team: int) -> MyPlayer:
        my_players = self._read_myteam() if team == 0 else self._read_youth_team()
        offset = 0x7051E0 if team == 0 else 0x70F0A8
        target_player = list(filter(lambda p: p.id.value == id, my_players)).pop()
        player = MyPlayer()
        player.index = target_player.index
        i = player.index
        player.id = self._read_int_byte(offset + i * 0x240, 2)
        player.pos = self._read_int_byte(offset + 2 + i * 0x240)
        player.age = self._read_int_byte(offset + 3 + i * 0x240)
        player.name = self._read_str_byte(offset + 0x186 + i * 0x240, 0xD)
        player.born = self._read_int_byte(offset + 0x193 + i * 0x240)
        player.born2 = self._read_int_byte(offset + 0x194 + i * 0x240)
        player.rank = self._read_int_byte(offset + 0x195 + i * 0x240)
        player.base_pos = self._read_int_byte(offset + 0x196 + i * 0x240)
        player.height = self._read_int_byte(offset + 0x198 + i * 0x240)
        player.number = self._read_int_byte(offset + 0x19A + i * 0x240)
        player.foot = self._read_int_byte(offset + 0x19B + i * 0x240)
        player.desire = self._read_int_byte(offset + 0x1AC + i * 0x240)
        player.pride = self._read_int_byte(offset + 0x1AD + i * 0x240)
        player.ambition = self._read_int_byte(offset + 0x1AE + i * 0x240)
        player.persistence = self._read_int_byte(offset + 0x1AF + i * 0x240)
        player.tone_type = self._read_int_byte(offset + 0x1B1 + i * 0x240)
        player.patient = self._read_int_byte(offset + 0x1B8 + i * 0x240)
        player.cooperation_type = self._read_int_byte(offset + 0x1BA + i * 0x240)
        player.wave_type = self._read_int_byte(offset + 0x1BB + i * 0x240)
        player.grow_type_phy = self._read_int_byte(offset + 0x1BC + i * 0x240)
        player.grow_type_tec = self._read_int_byte(offset + 0x1BD + i * 0x240)
        player.grow_type_sys = self._read_int_byte(offset + 0x1BE + i * 0x240)
        player.super_sub = self._read_int_byte(offset + 0x1BF + i * 0x240)
        player.wild_type = self._read_int_byte(offset + 0x1C1 + i * 0x240)
        player.weak_type = self._read_int_byte(offset + 0x1C2 + i * 0x240)
        player.tired_type = self._read_int_byte(offset + 0x1C3 + i * 0x240)
        player.style = self._read_int_byte(offset + 0x1C5 + i * 0x240)
        player.magic_value = self._read_int_byte(offset + 0x1CC + i * 0x240, 4)
        player.salary = self._read_int_byte(offset + 0x1D6 + i * 0x240, 2)
        player.offer_years_passed = self._read_int_byte(offset + 0x1D9 + i * 0x240)
        player.offer_years_total = self._read_int_byte(offset + 0x1DA + i * 0x240)
        player.comp_money = self._read_int_byte(offset + 0x1DE + i * 0x240, 2)
        player.comp_discord = self._read_int_byte(offset + 0x1E0 + i * 0x240, 2)
        player.comp_staff = self._read_int_byte(offset + 0x1E2 + i * 0x240, 2)
        player.comp_usage = self._read_int_byte(offset + 0x1E4 + i * 0x240, 2)
        player.comp_result = self._read_int_byte(offset + 0x1E6 + i * 0x240, 2)
        player.comp_status = self._read_int_byte(offset + 0x1E8 + i * 0x240, 2)
        player.comp_euipment = self._read_int_byte(offset + 0x1EA + i * 0x240, 2)
        player.pop = self._read_int_byte(offset + 0x1EC + i * 0x240, 2)
        player.tired = self._read_int_byte(offset + 0x1F2 + i * 0x240, 2)
        player.status = self._read_int_byte(offset + 0x1F4 + i * 0x240, 2)
        player.condition = self._read_int_byte(offset + 0x1F6 + i * 0x240, 2)
        player.moti = self._read_int_byte(offset + 0x1F8 + i * 0x240, 4)
        player.power = self._read_int_byte(offset + 0x204 + i * 0x240, 2)
        player.kan = self._read_int_byte(offset + 0x206 + i * 0x240, 2)
        player.return_days = self._read_int_byte(offset + 0x208 + i * 0x240, 2)
        player.abroad_times = self._read_int_byte(offset + 0x211 + i * 0x240)
        player.explosion_exp = self._read_int_byte(offset + 0x222 + i * 0x240, 2)
        player.explosion_level = self._read_int_byte(offset + 0x224 + i * 0x240)
        player.explo_countdown = self._read_int_byte(offset + 0x225 + i * 0x240)
        player.explo_pending_reason = self._read_int_byte(offset + 0x226 + i * 0x240)
        player.explo_final_reason = self._read_int_byte(offset + 0x227 + i * 0x240)
        player.style_equip = self._read_int_byte(offset + 0x228 + i * 0x240)
        player.style_learned1 = self._read_int_byte(offset + 0x22C + i * 0x240, 4)
        player.style_learned2 = self._read_int_byte(offset + 0x230 + i * 0x240, 4)
        player.style_learned3 = self._read_int_byte(offset + 0x234 + i * 0x240, 4)
        player.style_learned4 = self._read_int_byte(offset + 0x238 + i * 0x240, 4)
        player.abilities = []
        for j in range(0x40):
            current = self._read_int_byte(offset + 4 + i * 0x240 + j * 6, 2)
            current_max = self._read_int_byte(offset + 6 + i * 0x240 + j * 6, 2)
            max = self._read_int_byte(offset + 8 + i * 0x240 + j * 6, 2)
            player.abilities.append(MyPlayerAbility(j, current, current_max, max))
        return player

    def _read_town(self) -> Town:
        start = 0x7354F0
        town = Town()
        town.living = self._read_int_byte(start + 2, 2)  # 2(2)
        town.economy = self._read_int_byte(start + 4, 2)  # 4(2)
        town.sports = self._read_int_byte(start + 6, 2)  # 6(2)
        town.env = self._read_int_byte(start + 8, 2)  # 8(2)
        town.population = self._read_int_byte(start + 0xC, 4)  # 0xc(4)
        town.price = self._read_int_byte(start + 0x10)  # 0x10
        town.traffic_level = self._read_int_byte(start + 0x11)  # 0x11
        town.soccer_pop = self._read_int_byte(start + 0x12)  # 0x12
        town.soccer_level = self._read_int_byte(start + 0x1C, 2)  # 0x1c(2)
        town.town_type = self._read_int_byte(start + 0x3D, 1)  # 0x3d(1)
        return town

    def _read_my_scout(self) -> list[MyScout]:
        start = 0x71288C
        scout_list = []
        for i in range(3):
            name = self._read_str_byte(start + i * 156 + 2, 0xD)
            born = self._read_int_byte(start + i * 156 + 0xf, 0x1)
            id = self._read_int_byte(start + i * 156 + 0x36, 2)
            age = self._read_int_byte(start + i * 156 + 0x10, 1)
            rank = self._read_int_byte(start + i * 156 + 0x11, 1)
            abilities = []
            for j in range(21):
                ability = self._read_int_byte(start + i * 156 + 0x1E + j, 1)
                abilities.append(ability)
            area1 = self._read_int_byte(start + i * 156 + 0x34, 1)
            area2 = self._read_int_byte(start + i * 156 + 0x35, 1)
            salary = self._read_int_byte(start + i * 156 + 0x14, 2)
            contract_years = self._read_int_byte(start + i * 156 + 0x38, 1)
            offer_years = self._read_int_byte(start + i * 156 + 0x39, 1)
            my_scout = MyScout(id, age, offer_years, born=born)
            my_scout.saved_name = name
            my_scout.abilities = abilities
            my_scout.area1 = area1
            my_scout.area2 = area2
            my_scout.rank = rank
            my_scout.salary = salary
            my_scout.contract_years = contract_years
            scout_list.append(my_scout)
        return scout_list

    def _read_scout_candidates(self) -> list[MyScout]:
        start = 0x712A60
        scout_candidates = []
        for i in range(0xA):
            scout_id = self._read_int_byte(start + i * 4, 2)
            if scout_id and scout_id.value != 0xFFFF:
                offer_years = self._read_int_byte(start + i * 4 + 2, 1)
                age = self._read_int_byte(start + i * 4 + 3, 1)
                scout = MyScout(scout_id, age, offer_years)
                scout_candidates.append(scout)
        return scout_candidates

    def _read_album_players(self) -> list[IntByteField]:
        start = 0x260D4 + 0x705104
        r = []
        for i in range(9):
            r.append(self._read_int_byte(start + i * 4, 4))
        return r

    def _read_my_abroads(self) -> list[IntByteField]:
        start = 0x84C + 0x76397C
        abroad_list = []
        for i in range(70):
            a = self._read_int_byte(start + i * 4, 2)
            abroad_list.append(a)
        return abroad_list

    def _read_my_camps(self) -> list[IntByteField]:
        start = 0x964 + 0x76397C
        camp_list = []
        for i in range(40):
            a = self._read_int_byte(start + i * 4, 2)
            camp_list.append(a)
        return camp_list

    def _read_transfer_players(self) -> list[OtherPlayer]:
        start = 0xD7C4 + 0x705104
        players = []
        for i in range(3):
            for j in range(5):
                pid = self._read_int_byte(start + i * 156 + j * 14, 2)  # 0xd7c4(2)
                if pid.value != 0xFFFF:
                    age = self._read_int_byte(start + i * 156 + j * 14 + 5, 1)  # 0xd7c9(1)
                    player = OtherPlayer(pid, age)
                    players.append(player)
        return players

    def _read_free_players(self) -> list[OtherPlayer]:
        start = 0x26BF0 + 0x705104
        players = []
        for i in range(16):
            pid = self._read_int_byte(start + i * 14, 2)  # 0x26bf0(2)
            if pid.value != 0xFFFF:
                age = self._read_int_byte(start + i * 14 + 5, 1)  # 0x26bf5(1)
                player = OtherPlayer(pid, age)
                players.append(player)
        return players

    def _read_rookie_players(self) -> list[OtherPlayer]:
        start = 0x26CD0 + 0x705104
        players = []
        for i in range(36):
            pid = self._read_int_byte(start + i * 14, 2)  # 0x26cd0(2)
            if pid.value != 0xFFFF:
                age = self._read_int_byte(start + i * 14 + 5, 1)  # 0x26cd5(1)
                player = OtherPlayer(pid, age)
                players.append(player)
        return players

    def _read_my_coaches(self, offset: int, size: int) -> list[MyCoach]:
        result = []
        for i in range(size):
            coach_id = self._read_int_byte(offset + i * 0x84 + 0x6a, 2)  # 0x3e38(2)
            if coach_id.value == 0 or coach_id.value == 0xFFFF:
                continue
            coach_name = self._read_str_byte(offset + i * 0x84 + 2, 0xD)
            coach_born = self._read_int_byte(offset + i * 0x84 + 0xf, 0x1)  # 0x3dd0
            coach_rank = self._read_int_byte(offset + i * 0x84 + 0x10, 1)  # 0x3dd1
            coach_type = self._read_int_byte(offset + i * 0x84 + 0x11, 1)  # 0x3dd2
            coach_age = self._read_int_byte(offset + i * 0x84 + 0x12, 1)  # 0x3dd3
            offer_years = self._read_int_byte(offset + i * 0x84 + 0x6d, 1)  # 0x3e3b
            abilities = []
            for j in range(0x35):
                ability = self._read_int_byte(offset + i * 0x84 + 0x2c + j, 1)  # 0x3dfa
                abilities.append(ability)
            contract_years = self._read_int_byte(offset + i * 0x84 + 0x6c, 1)  # 0x3e3a
            salary = self._read_int_byte(offset + i * 0x84 + 0x1e, 2)  # 0x3dec
            sp_prac1 = self._read_int_byte(offset + i * 0x84 + 0x61, 1)  # 0x3e2f
            sp_prac2 = self._read_int_byte(offset + i * 0x84 + 0x62, 1)  # 0x3e30
            activate_plan = self._read_int_byte(offset + i * 0x84 + 0x28, 1)
            training_plan = self._read_int_byte(offset + i * 0x84 + 0x2a, 1)
            training_strength = self._read_int_byte(offset + i * 0x84 + 0x2b, 1)
            styles = []
            for j in range(6):
                style = self._read_int_byte(offset + i * 0x84 + 0x63 + j, 1)
                styles.append(style)
            coach = MyCoach(id=coach_id, age=coach_age, offer_years=offer_years)
            coach.saved_name = coach_name
            coach.rank = coach_rank
            coach.abilities = abilities
            coach.contract_years = contract_years
            coach.salary = salary
            coach.sp_prac1 = sp_prac1
            coach.sp_prac2 = sp_prac2
            coach.coach_type = coach_type
            coach.born = coach_born
            coach.styles = styles
            coach.activate_plan = activate_plan
            coach.training_plan = training_plan
            coach.training_strength = training_strength
            result.append(coach)
        return result

    def _read_coaches(self) -> list[MyCoach]:
        my_coaches = []
        my_coaches.extend(self._read_my_coaches(0x708F8E, 1))  # master coach
        my_coaches.extend(self._read_my_coaches(0x712a88, 4))  # coaches
        return my_coaches

    def _read_coach_candidates(self) -> list[MyCoach]:
        start = 0x71273c
        coach_candidates = []
        temp_coach_indexes = []
        for i in range(0x12):
            coach_id = self._read_int_byte(start + i * 4, 2)
            if coach_id.value == 0 or coach_id.value == 0xFFFF:
                continue
            offer_years = self._read_int_byte(start + i * 4 + 2, 1)
            age = self._read_int_byte(start + i * 4 + 3, 1)
            coach_candidates.append(MyCoach(id=coach_id, age=age, offer_years=offer_years))
            temp_coach_indexes.append(i)
        start = 0x712784
        for i in range(0x16):
            for j in range(3):
                coach_id = self._read_int_byte(start + i * 12 + j * 4, 2)
                if i in temp_coach_indexes and coach_id and coach_id.value != 0xFFFF:
                    offer_years = self._read_int_byte(start + i * 12 + j * 4 + 2, 1)
                    age = self._read_int_byte(start + i * 12 + j * 4 + 3, 1)
                    coach_candidates.append(MyCoach(id=coach_id, age=age, offer_years=offer_years))
        return coach_candidates

    def _read_draft_players(self) -> list[OtherPlayer]:
        month = self._read_int_byte(0x703D52)
        date = self._read_int_byte(0x703D53)
        if month.value == 1 and date.value <= 15 and date.value > 1:
            start = 0x69E434
            players = []
            for i in range(40):
                pid = self._read_int_byte(start + i * 0x328, 2)
                if pid.value != 0 and pid.value != 0xFFFF:
                    age = self._read_int_byte(start + i * 0x328 + 3, 1)
                    player = OtherPlayer(pid, age)
                    players.append(player)
            return players
        return []

    def _read_youth_candidates(self) -> list[OtherPlayer]:
        year = self._read_int_byte(0x703D50, 2)
        set = (year.value - 2003 + 2) % 3
        start = 0x72C75E
        players = []
        for i in range(12):
            pid = self._read_int_byte(start + i * 6 + set * 2, 2)
            if pid.value != 0 and pid.value != 0xFFFF:
                player = OtherPlayer(pid, IntByteField(1, 16, 0))
                players.append(player)
        return players

    def _read_sponsors(self, size: int, address: int) -> list[SponsorDto]:
        sponsors = []
        if size > 0 and address > 0:
            for i in range(size):
                offset = address + i * 10
                sponsor_id = self._read_int_byte(offset, 1).value
                if sponsor_id == 0 or sponsor_id == 0xFF:
                    continue
                contract_years = self._read_int_byte(offset + 1, 1).value
                offer_years = self._read_int_byte(offset + 2, 1).value
                amount = self._read_int_byte(offset + 6, 2).value
                amount_high = amount * 100 // 10000
                amount_low = amount * 100 % 10000
                sponsors.append(
                    SponsorDto(
                        id=sponsor_id, contract_years=contract_years, offer_years=offer_years, amount_high=amount_high, amount_low=amount_low
                    )
                )
        return sponsors

    def _read_my_sponsors(self) -> list[SponsorDto]:
        start = 0x715070
        size = 7
        return self._read_sponsors(size, start)

    def _read_candidate_sponsors(self, size_addr: int, base_addr: int) -> list[SponsorDto]:
        size = self._read_int_byte(size_addr, 4).value
        address = self._read_int_byte(base_addr, 4).value
        return self._read_sponsors(size, address)

    def _read_main_candidate_sponsors(self) -> list[SponsorDto]:
        return self._read_candidate_sponsors(0x0061D2E8, 0x0061D2EC)

    def _read_sub_candidate_sponsors(self) -> list[SponsorDto]:
        return self._read_candidate_sponsors(0x0061D2F0, 0x0061D2F4)

    def check_connect(self) -> bool:
        try:
            status = self._get_emu_status()
            is_connected = status in [1, 0]
            if is_connected:
                ver = self.game_ver()
                CnVer.set_ver(ver)
                Reseter.reset()
                return True
            self.reset()
            return False
        except Exception as e:
            print(f"Error getting emulator status: {e}")
            self.reset()
            return False

    @override
    def games(self) -> list[str]:
        return []

    @override
    def select_game(self, game: str) -> int:
        return self.game_ver()

    @override
    def read_club(self) -> ClubDto:
        club = self._read_club()
        return club.to_dto()

    @override
    def read_myteam(self) -> list[MyTeamPlayerDto]:
        my_players = self._read_myteam()
        result = []
        for player in [player for player in my_players if player.id.value != 0xFFFF]:
            result.append(MyTeamPlayerDto(id=player.id.value, name=player.name.value, pos=player.pos.value))
        return sorted(result, key=lambda player: player.pos)

    @override
    def read_youth_team(self) -> list[MyTeamPlayerDto]:
        my_players = self._read_youth_team()
        result = []
        for player in [player for player in my_players if player.id.value != 0xFFFF]:
            result.append(MyTeamPlayerDto(id=player.id.value, name=player.name.value, pos=player.pos.value))
        return sorted(result, key=lambda player: player.pos)

    @override
    def read_national_team(self) -> list[MyTeamPlayerDto]: ...

    @override
    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        players = self._read_other_team_players(team_index)
        result = []
        my_album_players = self.read_my_album_players()
        for player in [player for player in players if player.id.value != 0xFFFF]:
            player_dto = player.to_dto()
            player_dto.my_album_players = my_album_players
            result.append(player_dto)
        return sorted(result, key=lambda player: player.pos)

    @override
    def read_other_team_friendly(self, team_index: int) -> int:
        return self._read_other_team_friendly(team_index).value

    @override
    def read_myplayer(self, id: int, team: int) -> MyPlayerDto:
        return self._read_myplayer(id, team).to_dto()

    @override
    def read_scouts(self, type: int) -> list[ScoutDto]:
        scouts = (
            [f.to_dto() for f in self._read_my_scout()]
            if type == 0
            else [f.to_dto_with_name(f.id.value) for f in self._read_scout_candidates()]
        )
        return scouts

    @override
    def read_scout(self, id: int, type: int) -> ScoutDto:
        scouts = self.read_scouts(type)
        scout = next((s for s in scouts if s.id == id), None)
        assert scout is not None, f"Scout with id {id} not found."
        excls = scout_excl_tbl.get(scout.id, [])
        simi_excls = scout_simi_excl_tbl.get(scout.id, [])
        if not excls and not simi_excls:
            return scout
        other_teams = self._read_other_teams()
        for i, team in enumerate(other_teams):
            team.players = self._read_other_team_players(i)
        def resolve_players(player_ids: list[int]) -> list[SearchDto]:
            result = []
            for pid in player_ids:
                dto = SearchDto(name=Player(pid).name)
                for team in other_teams:
                    if team.players:
                        for player in team.players:
                            if player.id.value == pid:
                                dto.age = player.age.value
                                dto.team_id = team_ids.index(team.id.value)
                                break
                result.append(dto)
            return result
        scout.exclusive_players = resolve_players(excls)
        scout.simi_exclusive_players = resolve_players(simi_excls)
        return scout

    @override
    def read_coaches(self, type: int) -> list[CoachDto]:
        coaches = (
            [f.to_dto() for f in self._read_coaches()]
            if type == 0
            else [f.to_dto_with_name(f.id.value) for f in self._read_coach_candidates()]
        )
        return coaches

    @override
    def read_coach(self, id: int, type: int) -> CoachDto:
        coaches = self.read_coaches(type)
        coach = next((s for s in coaches if s.id == id), None)
        assert coach is not None, f"Coach with id {id} not found."
        coach.enabled_abr_ids = [f.id for f in self.read_my_abroads(0) if f.is_enabled]
        coach.enabled_camp_ids = [f.id for f in self.read_my_abroads(1) if f.is_enabled]
        return coach

    @override
    def read_my_abroads(self, type: int) -> list[AbroadDto]:
        dtos = AbroadDto.get_abr_teams() if type == 0 else AbroadDto.get_camp_teams()
        abr_camp_list = self._read_my_abroads() if type == 0 else self._read_my_camps()
        for i, dto in enumerate(dtos):
            dto.is_enabled = abr_camp_list[i].value != 0
        return dtos

    @override
    def read_one_abroad(self, index: int, type: int) -> AbroadDto:
        return AbroadDto.get_abr_camp_dto(index, type)

    @override
    def read_town(self) -> TownDto:
        return self._read_town().to_dto()

    @override
    def read_my_album_players(self) -> list[int]:
        players_raw = [p.value for p in self._read_album_players()]
        byte_data = bytearray()
        for val in players_raw:
            byte_data.extend(struct.pack("<I", val))
        return get_album_bit_indices(byte_data)

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
        other_team_players: list[list[OtherPlayer]] = []
        ids = []
        tmp_players = []
        match scout_action:
            case None | 0:
                for i in range(0x109):
                    players = self._read_other_team_players(i)
                    other_team_players.append(players)
                for team in other_team_players:
                    for player in team:
                        if player.id.value != 0xFFFF:
                            if age and age != player.age.value:
                                continue
                            ids.append(player.id.value)
            case 1:
                tmp_players = self._read_transfer_players()
            case 2:
                tmp_players = self._read_free_players()
            case 3:
                tmp_players = self._read_rookie_players()
            case 4:
                tmp_players = self._read_draft_players()
            case 5:
                tmp_players = self._read_youth_candidates()
        for p in tmp_players:
            ids.append(p.id.value)
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
            for i, team in enumerate(other_team_players):
                for player in team:
                    if player.id.value in filter_ids:
                        dto = player.to_dto()
                        if _match_filters(dto):
                            dto.team_index = i
                            result.append(dto)
        else:
            filter_players = [f for f in tmp_players if f.id.value in filter_ids]
            for p in filter_players:
                dto = p.to_dto()
                if _match_filters(dto):
                    dto.team_index = -1
                    result.append(dto)
        my_album_players = self.read_my_album_players()
        for player in result:
            player.my_album_players = my_album_players
        return sorted(result, key=lambda player: player.pos)

    @override
    def save_club(self, club_data: ClubDto) -> bool:
        club = self._read_club()
        club.funds.value = club_data.combo_funds()
        club.year.value = club_data.year + 2003
        club.difficulty.value = club_data.difficulty
        bytes_fields = []
        bytes_fields.append(club.funds)
        bytes_fields.append(club.year)
        bytes_fields.append(club.difficulty)
        self._save(bytes_fields)
        return True

    @override
    def save_player(self, data: MyPlayerDto, team: int) -> bool:
        player = self._read_myplayer(data.id, team)
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
        byte_field = self._read_other_team_friendly(team_index)
        byte_field.value = friendly
        bits_fields = []
        bits_fields.append(byte_field)
        self._save(bits_fields)
        return True

    @override
    def save_town(self, data: TownDto) -> bool:
        town = self._read_town()
        town.living.value = data.living
        town.economy.value = data.economy
        town.sports.value = data.sports
        town.env.value = data.env
        town.population.value = data.population
        town.price.value = data.price
        town.traffic_level.value = data.traffic_level
        town.soccer_pop.value = data.soccer_pop
        town.soccer_level.value = data.soccer_level
        bits_fields = []
        bits_fields.append(town.living)
        bits_fields.append(town.economy)
        bits_fields.append(town.sports)
        bits_fields.append(town.env)
        bits_fields.append(town.population)
        bits_fields.append(town.price)
        bits_fields.append(town.traffic_level)
        bits_fields.append(town.soccer_pop)
        bits_fields.append(town.soccer_level)
        self._save(bits_fields)
        return True

    @override
    def read_sponsors(self, type: int) -> list[SponsorDto]:
        if type == 0:
            sponsors = self._read_my_sponsors()
        else:
            sponsors = self._read_main_candidate_sponsors()
            sponsors.extend(self._read_sub_candidate_sponsors())
        if not sponsors:
            return []
        my_abroads = [f.id for f in self.read_my_abroads(0) if f.is_enabled]
        my_camps = [f.id for f in self.read_my_abroads(1) if f.is_enabled]
        for sponsor in sponsors:
            sponsor.enabled_abr_ids = my_abroads
            sponsor.enabled_camp_ids = my_camps
        return sponsors

    @override
    def reset(self):
        if not self.destroyed:
            try:
                self.libipc.pine_pcsx2_delete(self.ipc)
            finally:
                self.destroyed = True

    @override
    def game_ver(self) -> int:
        uuid = self.libipc.pine_getgameuuid(self.ipc, False)
        if uuid == b"d70c3195":
            return 0
        test_char = self._read_int_byte(0x5DA110, 2)
        if test_char.value == int.from_bytes(b"\x96\xa5", byteorder="little"):
            return 2
        return 1

    def _save(self, bytes_fields: list[IntByteField | StrByteField]):
        for field in bytes_fields:
            if isinstance(field, IntByteField):
                self._write_int_byte(field)
            else:
                self._write_str_byte(field)
