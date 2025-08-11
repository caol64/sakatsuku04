import ctypes
import importlib.resources
import platform
from ctypes import c_bool, c_char, c_char_p, c_uint, c_ulong, c_void_p
import struct

from ..data_reader import DataReader
from ..dtos import AbroadDto, ClubDto, MyPlayerDto, MyTeamPlayerDto, OtherTeamPlayerDto, ScoutDto, SearchDto, TownDto
from ..io import CnVer, IntByteField, StrByteField
from ..objs import Player, Reseter
from ..utils import find_name_matches, get_album_bit_indices
from ..constants import scout_excl_tbl, scout_simi_excl_tbl, team_ids
from .models import Club, MyPlayer, MyPlayerAbility, MyScout, OtherPlayer, OtherTeam, Sche, Town


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
        self._read_funcs = {
            1: self._read_8bit,
            2: self._read_16bit,
            4: self._read_32bit,
        }
        self._write_funcs = {
            1: self._write_8bit,
            2: self._write_16bit,
            4: self._write_32bit,
        }

    def _read_8bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(0), False)

    def _read_16bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(1), False)

    def _read_32bit(self, address: int) -> int:
        return self.libipc.pine_read(self.ipc, address, c_char(2), False)

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
        self._write_funcs[byte_field.byte_length](
            byte_field.byte_offset, byte_field.value
        )

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
        club.team_status = self._read_int_byte(0x70e676, 2)
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
        other_teams: list[OtherTeam] = list()
        for i in range(0x109):  # loop the teams
            id = self._read_int_byte(0x72C7F0 + i * 0x6C, 2)
            unknown1 = self._read_int_byte(0x72C856 + i * 0x6C, 2)
            unknown2 = self._read_int_byte(0x72C858 + i * 0x6C, 2)
            friendly = self._read_int_byte(0x72C85A + i * 0x6C, 2)
            other_team = OtherTeam(i, id, friendly, unknown1, unknown2, [])
            other_teams.append(other_team)
        # 7337bc
        return other_teams

    def _read_other_team_players(self, team_index: int) -> list[OtherPlayer]:
        players = []
        for i in range(0x19):
            pid = self._read_int_byte(0x72C7F2 + team_index * 0x6C + i * 4, 2)
            age = self._read_int_byte(0x72C7F4 + team_index * 0x6C + i * 4)
            ability_graph = self._read_int_byte(0x72C7F5 + team_index * 0x6C + i * 4)
            number = self._read_int_byte(0x7337BC + team_index * 0x19 + i)
            player = OtherPlayer(pid, age, ability_graph, number)
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
        player.grow_type_id = self._read_int_byte(offset + 0x1BB + i * 0x240)
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
        start = 0x7354f0
        town = Town()
        town.living = self._read_int_byte(start + 2, 2) # 2(2)
        town.economy = self._read_int_byte(start + 4, 2) # 4(2)
        town.sports = self._read_int_byte(start + 6, 2) # 6(2)
        town.env = self._read_int_byte(start + 8, 2) # 8(2)
        town.population = self._read_int_byte(start + 0xc, 4) # 0xc(4)
        town.price = self._read_int_byte(start + 0x10) # 0x10
        town.traffic_level = self._read_int_byte(start + 0x11) # 0x11
        town.soccer_pop = self._read_int_byte(start + 0x12) # 0x12
        town.soccer_level = self._read_int_byte(start + 0x1c, 2) # 0x1c(2)
        town.town_type = self._read_int_byte(start + 0x3d, 1) # 0x3d(1)
        return town

    def _read_my_scout(self) -> list[MyScout]:
        start = 0x71288c
        scout_list = []
        for i in range(3):
            name = self._read_str_byte(start + i * 156 + 2, 0xD)
            id = self._read_int_byte(start + i * 156 + 0x36, 2)
            scout = MyScout(id)
            scout.saved_name = name
            scout_list.append(scout)
        return scout_list

    def _read_scout_candidates(self) -> list[MyScout]:
        start = 0x712a60
        scout_candidates = []
        for i in range(0xA):
            scout_id = self._read_int_byte(start + i * 4, 2)
            if scout_id and scout_id.value != 0xFFFF:
                scout = MyScout(scout_id)
                scout_candidates.append(scout)
        return scout_candidates

    def _read_album_players(self) -> list[IntByteField]:
        start = 0x260d4 + 0x705104
        r = []
        for i in range(9):
            r.append(self._read_int_byte(start + i * 4, 4))
        return r

    def _read_my_abroads(self) -> Sche:
        sche = Sche()
        start = 0x84c + 0x76397c
        sche.abroad_list = []
        for i in range(70):
            a = self._read_int_byte(start + i * 4, 2)
            sche.abroad_list.append(a)
        start = 0x964 + 0x76397c
        sche.camp_list = []
        for i in range(40):
            a = self._read_int_byte(start + i * 4, 2)
            sche.camp_list.append(a)
        return sche

    def _read_transfer_players(self) -> list[OtherPlayer]:
        start = 0xd7c4 + 0x705104
        players = []
        for i in range(3):
            for j in range(5):
                pid = self._read_int_byte(start + i * 156 + j * 14, 2) # 0xd7c4(2)
                if pid.value != 0xffff:
                    age = self._read_int_byte(start + i * 156 + j * 14 + 5, 1) # 0xd7c9(1)
                    player = OtherPlayer(pid, age)
                    players.append(player)
        return players

    def _read_free_players(self) -> list[OtherPlayer]:
        start = 0x26bf0 + 0x705104
        players = []
        for i in range(16):
            pid = self._read_int_byte(start + i * 14, 2) # 0x26bf0(2)
            if pid.value != 0xffff:
                age = self._read_int_byte(start + i * 14 + 5, 1) # 0x26bf5(1)
                player = OtherPlayer(pid, age)
                players.append(player)
        return players

    def _read_rookie_players(self) -> list[OtherPlayer]:
        start = 0x26cd0 + 0x705104
        players = []
        for i in range(36):
            pid = self._read_int_byte(start + i * 14, 2) # 0x26cd0(2)
            if pid.value != 0xffff:
                age = self._read_int_byte(start + i * 14 + 5, 1) # 0x26cd5(1)
                player = OtherPlayer(pid, age)
                players.append(player)
        return players

    def check_connect(self) -> bool:
        is_connected = False
        try:
            status = self._get_emu_status()
            is_connected = status in [1, 0]
            if is_connected:
                ver = self.game_ver()
                CnVer.set_ver(ver)
                Reseter.reset()
            return is_connected
        except Exception as e:
            print(f"Error getting emulator status: {e}")
            is_connected = False
            self.reset()
            return is_connected

    def games(self) -> list[str]:
        return []

    def select_game(self, game: str): ...

    def read_club(self) -> ClubDto:
        club = self._read_club()
        return club.to_dto()

    def read_myteam(self) -> list[MyTeamPlayerDto]:
        my_players = self._read_myteam()
        result = []
        for player in [player for player in my_players if player.id.value != 0xFFFF]:
            result.append(
                MyTeamPlayerDto(
                    id=player.id.value, name=player.name.value, pos=player.pos.value
                )
            )
        return sorted(result, key=lambda player: player.pos)

    def read_youth_team(self) -> list[MyPlayerDto]:
        my_players = self._read_youth_team()
        result = []
        for player in [player for player in my_players if player.id.value != 0xFFFF]:
            result.append(
                MyTeamPlayerDto(
                    id=player.id.value, name=player.name.value, pos=player.pos.value
                )
            )
        return sorted(result, key=lambda player: player.pos)

    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        players = self._read_other_team_players(team_index)
        result = []
        for player in [player for player in players if player.id.value != 0xFFFF]:
            result.append(player.to_dto())
        return sorted(result, key=lambda player: player.pos)

    def read_other_team_friendly(self, team_index: int) -> int:
        return self._read_other_team_friendly(team_index).value

    def read_myplayer(self, id: int, team: int) -> MyPlayerDto:
        return self._read_myplayer(id, team).to_dto()

    def read_scouts(self, type: int) -> list[ScoutDto]:
        scouts = (
            [f.to_dto() for f in self._read_my_scout()]
            if type == 0
            else [f.to_dto_with_name(f.id.value) for f in self._read_scout_candidates()]
        )

        if not scouts:
            return scouts

        other_teams = self._read_other_teams()
        for i, team in enumerate(other_teams):
            team.players = self._read_other_team_players(i)

        def resolve_players(player_ids: list[int]) -> list[SearchDto]:
            result = []
            for pid in player_ids:
                dto = SearchDto(name=Player(pid).name)
                for team in other_teams:
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

    def read_my_abroads(self, type: int) -> list[AbroadDto]:
        dtos = AbroadDto.get_abr_camp_teams(type)
        sche = self._read_my_abroads()
        for i, dto in enumerate(dtos):
            dto.is_enabled = sche.abroad_list[i].value != 0 if type == 0 else sche.camp_list[i].value != 0
        return dtos

    def read_one_abroad(self, index: int, type: int) -> AbroadDto:
        dto = AbroadDto.get_abr_camp_dto(index, type)
        return dto

    def read_town(self) -> TownDto:
        return self._read_town().to_dto()

    def read_my_album_players(self) -> list[int]:
        players_raw = [p.value for p in self._read_album_players()]
        byte_data = bytearray()
        for val in players_raw:
            byte_data.extend(struct.pack('<I', val))
        return get_album_bit_indices(byte_data)

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
        tmp_players = None
        if not scout_action:
            for i in range(0x109):
                players = self._read_other_team_players(i)
                other_team_players.append(players)
            for team in other_team_players:
                for player in team:
                    if player.id.value != 0xFFFF:
                        if age and age != player.age.value:
                            continue
                        ids.append(player.id.value)
        else:
            if scout_action == 1:
                tmp_players = self._read_transfer_players()
            elif scout_action == 2:
                tmp_players = self._read_free_players()
            elif scout_action == 3:
                tmp_players = self._read_rookie_players()
            for p in tmp_players:
                ids.append(p.id.value)
        filter_players = {k: v for k, v in Player.player_dict().items() if k in ids}
        filter_ids = find_name_matches(filter_players, name) if name else ids
        result = []
        def _match_filters(dto: OtherTeamPlayerDto) -> bool:
            if pos is not None and pos != dto.pos:
                return False
            if country is not None:
                if (country == 50 and dto.born > 50) or (country != 50 and dto.born != country):
                    return False
            if style is not None and style != dto.style:
                return False
            if tone is not None and tone != dto.tone_type:
                return False
            if cooperation is not None and cooperation != dto.cooperation_type:
                return False
            if rank is not None and rank != dto.rank:
                return False
            return True
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
        return result

    def save_club(self, club_data: ClubDto) -> bool:
        club = self._read_club()
        club.funds.value = club_data.combo_funds()
        club.year.value = club_data.year + 2003
        club.difficulty.value = club_data.difficulty
        bytes_fields = list()
        bytes_fields.append(club.funds)
        bytes_fields.append(club.year)
        bytes_fields.append(club.difficulty)
        self._save(bytes_fields)
        return True

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
            bits_fields.append(player.offer_years_passed)
            bits_fields.append(player.offer_years_total)

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
        byte_field = self._read_other_team_friendly(team_index)
        byte_field.value = friendly
        bits_fields = list()
        bits_fields.append(byte_field)
        self._save(bits_fields)
        return True

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
        bits_fields = list()
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

    def reset(self):
        self.libipc.pine_pcsx2_delete(self.ipc)

    def game_ver(self) -> int:
        uuid = self.libipc.pine_getgameuuid(self.ipc, False)
        if uuid == b"d70c3195":
            return 0
        else:
            test_char = self._read_int_byte(0x5da110, 2)
            if test_char.value == int.from_bytes(b'\x96\xA5', byteorder='little'):
                return 2
            else:
                return 1

    def _save(self, bytes_fields: list[IntByteField | StrByteField]):
        for field in bytes_fields:
            if isinstance(field, IntByteField):
                self._write_int_byte(field)
            else:
                self._write_str_byte(field)
