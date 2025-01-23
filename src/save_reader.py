import struct

from crc import CrcCaculator
from enc_dec import Blowfish

class SaveReader:
    FILE_SIZE = 523276
    DECODED_SIZE = FILE_SIZE - 12
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

    def build_crc(self, byte_array: bytes) -> bytes:
        crc_calc = CrcCaculator()
        left, right = crc_calc.calc(byte_array)
        return struct.Struct("<II").pack(left, right)

    def read(self, length: int) -> bytes:
        return self.data_buffer[self.read_offset: self.read_offset + length]

    def dec(self):
        blowfish = Blowfish()
        while self.read_offset < SaveReader.DECODED_SIZE:
            byteval = self.read(8)
            left, right = struct.unpack('<II', byteval)
            decrypted_left, decrypted_right = blowfish.de(left, right)
            self.decode_buffer += decrypted_right.to_bytes(4, byteorder="little")
            self.decode_buffer += decrypted_left.to_bytes(4, byteorder="little")
            self.read_offset += 8
        self.data_start = int.from_bytes(self.decode_buffer[:4], 'little') + 16

    def enc(self) -> bytes:
        blowfish = Blowfish()
        read_offset = 0
        encode_buffer = bytearray()
        while read_offset < SaveReader.DECODED_SIZE:
            byteval1 = self.decode_buffer[read_offset: read_offset + 4]
            byteval2 = self.decode_buffer[read_offset + 4: read_offset + 8]
            left = int.from_bytes(byteval1, 'little')
            right = int.from_bytes(byteval2, 'little')
            encrypted_left, encrypted_right = blowfish.en(left, right)
            encode_buffer += encrypted_right.to_bytes(4, byteorder="little")
            encode_buffer += encrypted_left.to_bytes(4, byteorder="little")
            read_offset += 8
        return bytes(encode_buffer)

    def decoded_data(self):
        return self.decode_buffer[self.data_start:]

    def update_decode_buffer(self, byte_array: bytes):
        assert len(self.decode_buffer) == self.data_start + len(byte_array)
        self.decode_buffer[self.data_start:] = byte_array

    def export_decode_buffer(self, path: str):
        with open(path, "wb") as f:
            f.write(self.decode_buffer)

    def export_decode_data(self, path: str):
        with open(path, "wb") as f:
            f.write(self.decoded_data())

    def build_save_bytes(self, byte_array: bytes) -> bytes:
        assert len(byte_array) == SaveReader.DECODED_SIZE
        crc = self.build_crc(byte_array)
        head = b'\x00\xfc\x07\x00'
        result = bytearray(head)
        result += byte_array[:261632]
        result += crc
        result += byte_array[261632:]
        return bytes(result)