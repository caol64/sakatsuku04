from pathlib import Path
from const import Const
from utils import decode_bytes_to_str, zero_terminate


class PlayerDataReader:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file = None

    def load(self):
        self.file = open(self.file_path, "rb")

    def read_player(self, uid: int) -> 'PlayerData':
        self.file.seek(PlayerData.START_OFFSET + uid * PlayerData.BLOCK_SIZE)
        return PlayerData(self.file.read(PlayerData.BLOCK_SIZE))
    
    def close(self):
        if self.file:
            self.file.close()


class PlayerData:

    START_OFFSET = 0x3232000
    BLOCK_SIZE = 0x48
    NAME_SIZE = 0xc

    def __init__(self, byte_val: bytes):
        self.byte_val = byte_val
        self.id = ''
        self.offset = 0
        self.name = self.decode_str(self.__read_bytes(PlayerData.NAME_SIZE))
        self.data: list[(str, int)] = list()
        for i in range(PlayerData.BLOCK_SIZE - PlayerData.NAME_SIZE):
            self.data.append((Const.ABILITY_LIST1[i], self.__read_int(1)))

    def __repr__(self):
        return f'''
        {self.name} (
            data: {self.data}
        )'''

    def decode_str(self, str: bytes) -> str:
        return zero_terminate(decode_bytes_to_str(str))

    def __read_bytes(self, n) -> bytes:
        result = self.byte_val[self.offset: self.offset + n]
        self.offset += n
        return result

    def __read_int(self, n) -> int:
        result = int.from_bytes(self.byte_val[self.offset: self.offset + n], byteorder='little', signed=False)
        self.offset += n
        return result

