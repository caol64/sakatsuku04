import struct

from crc import CrcCaculator
from enc_dec import Blowfish

class SaveReader:
    FILE_SIZE = 523276
    DATA_STRUCT = struct.Struct("<I261632sQ261632s") # (523276 - 12) / 2 = 261632
    DATA_SIZE = 0x0005EA10

    def __init__(self, byte_array: bytes):
        assert SaveReader.FILE_SIZE == len(byte_array)
        header, buffer1, crc, buffer2 = SaveReader.DATA_STRUCT.unpack(byte_array)
        self.data_buffer = bytearray()
        self.data_buffer += buffer1
        self.data_buffer += buffer2
        self.crc = crc
        assert header == len(self.data_buffer)
        self.decode_buffer = bytearray()
        self.read_offset = 0
        self.data_start = 0
        self.bit_stream = None

    def check_crc(self):
        crc_calc = CrcCaculator()
        left, right = crc_calc.calc(self.data_buffer)
        assert self.crc == (right << 32) | left

    def read(self, length: int) -> bytes:
        return self.data_buffer[self.read_offset: self.read_offset + length]

    def dec(self):
        blowfish = Blowfish()
        while self.read_offset < SaveReader.DATA_SIZE:
            byteval = self.read(8)
            left, right = struct.unpack('<II', byteval)
            decrypted_left, decrypted_right = blowfish.de(left, right)
            self.decode_buffer += decrypted_right.to_bytes(4, byteorder="little")
            self.decode_buffer += decrypted_left.to_bytes(4, byteorder="little")
            self.read_offset += 8
        self.data_start = int.from_bytes(self.decode_buffer[:4], 'little') + 16

    def decoded_data(self):
        return self.decode_buffer[self.data_start:]

    def export_decode_buffer(self, path: str):
        with open(path, "wb") as f:
            f.write(self.decode_buffer)

    def export_decode_data(self, path: str):
        with open(path, "wb") as f:
            f.write(self.decoded_data())