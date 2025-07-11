import ctypes
import platform
import importlib.resources
from ctypes import c_char_p, c_void_p, c_uint, c_ulong, c_char, c_bool

from ..utils import find_name_matches
from .models import Club, MyPlayer, OtherTeam, OtherPlayer, MyPlayerAbility
from ..io import IntByteField, StrByteField, CnVer
from ..data_reader import DataReader
from ..dtos import ClubDto, MyPlayerDto, MyTeamPlayerDto, OtherTeamPlayerDto, SearchDto
from ..objs import Player, Position


class Pcsx2DataReader(DataReader):

    def __init__(self):
        # we get the correct library extension per os
        lib="libpine_c"
        cur_os = platform.system()
        if(cur_os == "Linux"):
            lib="libpine_c.so"
        elif(cur_os == "Windows"):
            lib="pine_c.dll"
        elif(cur_os == "Darwin"):
            lib="libpine_c.dylib"
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
            result += int_value.to_bytes(1, 'little')
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
        return club

    def _read_myteam(self) -> list[MyPlayer]:
        my_players = []
        for i in range(0x19):
            player = MyPlayer()
            player.index = i
            player.id = self._read_int_byte(0x7051E0 + i * 0x240, 2)
            player.pos = self._read_int_byte(0x7051E2 + i * 0x240)
            player.name = self._read_str_byte(0x705366 + i * 0x240, 0xd)
            my_players.append(player)
        return my_players

    def _read_other_teams(self) -> list[OtherTeam]:
        other_teams: list[OtherTeam] = list()
        for i in range(0x109):  # loop the teams
            id = self._read_int_byte(0x72c7f0 + i * 0x6C, 2)
            unknown1 = self._read_int_byte(0x72C856 + i * 0x6C, 2)
            unknown2 = self._read_int_byte(0x72C858 + i * 0x6C, 2)
            friendly = self._read_int_byte(0x72C85A + i * 0x6C, 2)
            other_team = OtherTeam(i, id, friendly, unknown1, unknown2, [])
            other_teams.append(other_team)
        # 7337bc
        return other_teams

    def _read_other_team_players(self, team_index: int) -> list[OtherPlayer]:
        players = list()
        for i in range(0x19):
            pid = self._read_int_byte(0x72c7f2 + team_index * 0x6C + i * 4, 2)
            age = self._read_int_byte(0x72c7f4 + team_index * 0x6C + i * 4)
            ability_graph = self._read_int_byte(0x72c7f5 + team_index * 0x6C + i * 4)
            number = self._read_int_byte(0x7337bd + team_index * 0x19 + i * 1)
            player = OtherPlayer(pid, age, ability_graph, number)
            players.append(player)
        return players

    def _read_other_team_friendly(self, team_index: int) -> IntByteField:
        return self._read_int_byte(0x72c85a + team_index * 0x6C, 2)

    def _read_myplayer(self, id: int) -> MyPlayer:
        my_players = self._read_myteam()
        target_player = list(filter(lambda p: p.id.value == id, my_players)).pop()
        player = MyPlayer()
        player.index = target_player.index
        i = player.index
        player.id = self._read_int_byte(0x7051E0 + i * 0x240, 2)
        player.pos = self._read_int_byte(0x7051E2 + i * 0x240)
        player.age = self._read_int_byte(0x7051E3 + i * 0x240)
        player.name = self._read_str_byte(0x705366 + i * 0x240, 0xd)
        player.born = self._read_int_byte(0x705373 + i * 0x240)
        player.born2 = self._read_int_byte(0x705374 + i * 0x240)
        player.rank = self._read_int_byte(0x705375 + i * 0x240)
        player.pos2 = self._read_int_byte(0x705376 + i * 0x240)
        player.height = self._read_int_byte(0x705378 + i * 0x240)
        player.number = self._read_int_byte(0x70537A + i * 0x240)
        player.foot = self._read_int_byte(0x70537B + i * 0x240)
        player.desire = self._read_int_byte(0x70538B + i * 0x240)
        player.pride = self._read_int_byte(0x70538C + i * 0x240)
        player.ambition = self._read_int_byte(0x70538D + i * 0x240)
        player.persistence = self._read_int_byte(0x70538E + i * 0x240)
        player.tone_type = self._read_int_byte(0x705391 + i * 0x240)
        player.patient = self._read_int_byte(0x705397 + i * 0x240)
        player.cooperation_type = self._read_int_byte(0x70539A + i * 0x240)
        player.jl_factor = self._read_int_byte(0x70539B + i * 0x240)
        player.grow_type_phy = self._read_int_byte(0x70539C + i * 0x240)
        player.grow_type_tec = self._read_int_byte(0x70539D + i * 0x240)
        player.grow_type_sys = self._read_int_byte(0x70539E + i * 0x240)
        player.style = self._read_int_byte(0x7053A5 + i * 0x240)
        player.magic_value = self._read_int_byte(0x7053AC + i * 0x240, 4)
        player.abroad_days = self._read_int_byte(0x7053E8 + i * 0x240, 2)
        player.abroad_times = self._read_int_byte(0x7053F1 + i * 0x240)
        player.style_equip = self._read_int_byte(0x705408 + i * 0x240)
        player.style_learned1 = self._read_int_byte(0x70540c + i * 0x240, 4)
        player.style_learned2 = self._read_int_byte(0x705410 + i * 0x240, 4)
        player.style_learned3 = self._read_int_byte(0x705414 + i * 0x240, 4)
        player.style_learned4 = self._read_int_byte(0x705418 + i * 0x240, 4)
        player.abilities = []
        for j in range(0x40):
            current = self._read_int_byte(0x7051E4 + i * 0x240 + j * 6, 2)
            current_max = self._read_int_byte(0x7051E6 + i * 0x240 + j * 6, 2)
            max = self._read_int_byte(0x7051E8 + i * 0x240 + j * 6, 2)
            player.abilities.append(MyPlayerAbility(j, current, current_max, max))
        return player

    def check_connect(self) -> bool:
        is_connected = False
        try:
            status = self._get_emu_status()
            is_connected = status in [1, 0]
            return is_connected
        except Exception as e:
            print(f"Error getting emulator status: {e}")
            is_connected = False
            return is_connected
        finally:
            if not is_connected:
                self.reset()
            else:
                CnVer.is_cn = self.is_cn()
                Player.reset_player_dict()

    def games(self) -> list[str]:
        return []

    def select_game(self, game: str):
        ...

    def read_club(self) -> ClubDto:
        club = self._read_club()
        return club.to_dto()

    def read_myteam(self) -> list[MyTeamPlayerDto]:
        my_players = self._read_myteam()
        result = []
        for player in [
            player
            for player in my_players
            if player.id.value != 0xFFFF
        ]:
            result.append(MyTeamPlayerDto(id=player.id.value, name=player.name.value, pos=player.pos.value))
        return sorted(result, key=lambda player: player.pos)

    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        players = self._read_other_team_players(team_index)
        result = []
        for player in [
            player for player in players if player.id.value != 0xFFFF
        ]:
            result.append(player.to_dto())
        return sorted(result, key=lambda player: Position.ITEMS_REVERSE[player.pos])

    def read_other_team_friendly(self, team_index: int) -> int:
        return self._read_other_team_friendly(team_index).value

    def read_myplayer(self, id: int) -> MyPlayerDto:
        return self._read_myplayer(id).to_dto()

    def search_player(self, data: SearchDto) -> list[OtherTeamPlayerDto]:
        name = data.name
        pos = data.pos
        age = data.age
        other_team_players: list[list[OtherPlayer]] = []
        for i in range(0x109):
            players = self._read_other_team_players(i)
            other_team_players.append(players)
        ids = []
        for team in other_team_players:
            for player in team:
                if player.id.value != 0xFFFF:
                    if age and age != player.age.value:
                        continue
                    ids.append(player.id.value)
        filter_players = {k: v for k, v in Player.player_dict().items() if k in ids}
        filter_ids = find_name_matches(filter_players, name) if name else ids
        result = []
        for i, team in enumerate(other_team_players):
            for player in team:
                if player.id.value in filter_ids:
                    dto = player.to_dto()
                    dto.team_index = i
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

    def save_player(self, data: MyPlayerDto) -> bool:
        player = self._read_myplayer(data.id)
        if player:
            player.age.value = data.age
            player.abroad_times.value = data.abroad_times
            player.born.value = data.born
            player.born2.value = data.born
            player.pos.value = data.pos
            player.pos2.value = data.pos
            player.style.value = data.style
            player.style_equip.value = data.style
            player.set_style(data.style)
            player.cooperation_type.value = data.cooperation_type
            player.tone_type.value = data.tone_type
            player.grow_type_phy.value = data.grow_type_phy
            player.grow_type_tec.value = data.grow_type_tec
            player.grow_type_sys.value = data.grow_type_sys
            bits_fields = list()
            bits_fields.append(player.age)
            bits_fields.append(player.abroad_times)
            bits_fields.append(player.born)
            bits_fields.append(player.born2)
            bits_fields.append(player.pos)
            bits_fields.append(player.pos2)
            bits_fields.append(player.style)
            bits_fields.append(player.style_equip)
            bits_fields.append(player.style_learned1)
            bits_fields.append(player.style_learned2)
            bits_fields.append(player.cooperation_type)
            bits_fields.append(player.tone_type)
            bits_fields.append(player.grow_type_phy)
            bits_fields.append(player.grow_type_tec)
            bits_fields.append(player.grow_type_sys)

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

    def reset(self):
        self.libipc.pine_pcsx2_delete(self.ipc)

    def is_cn(self) -> bool:
        return self.libipc.pine_getgameuuid(self.ipc, False) != b'd70c3195'

    def _save(
        self,
        bytes_fields: list[IntByteField | StrByteField]
    ):
        for field in bytes_fields:
            if isinstance(field, IntByteField):
                self._write_int_byte(field)
            else:
                self._write_str_byte(field)

