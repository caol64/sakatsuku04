import ctypes
import platform
import importlib.resources
from ctypes import c_char_p, c_void_p, c_uint, c_ulong, c_char, c_bool

from .models import Club, MyPlayer, OtherTeam, OtherPlayer
from ..io import IntByteField, StrByteField
from ..data_reader import DataReader
from ..dtos import ClubDto, MyPlayerDto, OtherTeamPlayerDto
from ..objs import Position


class Pcsx2DataReader(DataReader):

    def __init__(self):
        # we get the correct library extension per os
        lib="libpine_c"
        cur_os = platform.system()
        if(cur_os == "Linux"):
            lib="libpine_c.so"
        elif(cur_os == "Windows"):
            lib="libpine_c.dll"
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

    def _write_32bit(self, address: int, value: int):
        self.libipc.pine_write(self.ipc, address, c_ulong(value), c_char(6), False)

    def _get_error(self) -> int:
        return self.libipc.pine_get_error(self.ipc)

    def _get_emu_status(self) -> int:
        return self.libipc.pine_status(self.ipc, False)

    def _read_int_byte(self, address: int, byte_length: int = 1) -> IntByteField:
        if byte_length not in self._read_funcs:
            raise ValueError(f"Unsupported byte length: {byte_length}")
        value = self._read_funcs[byte_length](address)
        return IntByteField(byte_length, value, address)

    def _read_str_byte(self, address: int, byte_length: int = 1) -> StrByteField:
        value = self._read_str(address, byte_length)
        return StrByteField(value, address)

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
        return club

    def _read_myteam(self) -> list[MyPlayer]:
        my_players = []
        for i in range(0x19):
            player = MyPlayer()
            player.index = i
            player.id = self._read_int_byte(0x7051E0 + i * 0x240, 2)
            player.pos = self._read_int_byte(0x7051E2 + i * 0x240)
            player.age = self._read_int_byte(0x7051E3 + i * 0x240)
            player.name = self._read_str_byte(0x705366 + i * 0x240, 0xd)
            player.number = self._read_int_byte(0x70537A + i * 0x240)
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

    def games(self) -> list[str]:
        return []

    def select_game(self, game: str):
        ...

    def read_club(self) -> ClubDto:
        club = self._read_club()
        return club.to_dto()

    def read_myteam(self) -> list[MyPlayerDto]:
        my_players = self._read_myteam()
        result = []
        for player in [
            player
            for player in my_players
            if player.id.value != 0xFFFF
        ]:
            result.append(player.to_dto())
        return sorted(result, key=lambda player: player.pos)

    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        players = self._read_other_team_players(team_index)
        result = []
        for player in [
            player for player in players if player.id.value != 0xFFFF
        ]:
            result.append(player.to_dto())
        return sorted(result, key=lambda player: Position.ITEMS_REVERSE[player.pos])

    def save_club(self, data: ClubDto) -> bool:
        ...

    def reset(self):
        self.libipc.pine_pcsx2_delete(self.ipc)

    def is_cn(self) -> bool:
        return self.libipc.pine_getgameuuid(self.ipc, False) != b'd70c3195'
