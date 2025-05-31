import csv
from pathlib import Path
from .utils import decode_bytes_to_str, get_resource_path, zero_terminate


class DataPacReader:
    """
    {52633600, 1028791, 0x45, 3, },	// data/etc/bpdata.bin
    """
    START_OFFSET = 0x3232000
    DATA_SIZE = 1028791
    PLAYER_COUNT = 0x2EC7

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file = None

    def load(self):
        self.file = open(self.file_path, "rb")

    def read(self) -> list['PlayerData']:
        read_offset = 0
        read_count = 0
        result = list()
        while read_count <= DataPacReader.PLAYER_COUNT:
            self.file.seek(DataPacReader.START_OFFSET + read_offset)
            player = PlayerData(self.file.read(PlayerData.BLOCK_SIZE))
            player.id = f"{read_count:04X}"
            result.append(player)
            read_offset += PlayerData.BLOCK_SIZE
            read_count += 1
        return result

    def read_player(self, uid: int) -> 'PlayerData':
        self.file.seek(DataPacReader.START_OFFSET + uid * PlayerData.BLOCK_SIZE)
        return PlayerData(self.file.read(PlayerData.BLOCK_SIZE))

    def close(self):
        if self.file:
            self.file.close()


class BaseData:
    def __init__(self, byte_val: bytes):
        self.byte_val = byte_val
        self.id = ''
        self.offset = 0
        self.name_bytes = self.read_bytes(PlayerData.NAME_SIZE)
        self.name = self.decode_str(self.name_bytes)

    def read_bytes(self, n) -> bytes:
        result = self.byte_val[self.offset: self.offset + n]
        self.offset += n
        return result

    def decode_str(self, str: bytes) -> str:
        return zero_terminate(decode_bytes_to_str(str))

    def read_int(self, n) -> int:
        result = int.from_bytes(self.byte_val[self.offset: self.offset + n], byteorder='little', signed=False)
        self.offset += n
        return result


class PlayerData(BaseData):

    BLOCK_SIZE = 0x48
    NAME_SIZE = 0xc
    _base_ablility_list = None

    @classmethod
    def base_ablility_list(cls) -> list[str]:
        if cls._base_ablility_list is None:
            cls._base_ablility_list = list()
            with open(get_resource_path('ability1.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 1:
                        cls._base_ablility_list.append(row[0])
        return cls._base_ablility_list

    def __init__(self, byte_val: bytes):
        super().__init__(byte_val)
        self.data: list[(str, int)] = list()
        for i in range(PlayerData.BLOCK_SIZE - PlayerData.NAME_SIZE):
            self.data.append((PlayerData.base_ablility_list()[i], self.read_int(1)))

    def __repr__(self):
        return f'''
        {self.name} (
            data: {self.data}
        )'''


class CoachData(BaseData):

    BLOCK_SIZE = 0x44
    NAME_SIZE = 0xc

    def __init__(self, byte_val: bytes):
        super().__init__(byte_val)


class ScoutData(BaseData):

    BLOCK_SIZE = 0x2b
    NAME_SIZE = 0xc

    def __init__(self, byte_val: bytes):
        super().__init__(byte_val)

