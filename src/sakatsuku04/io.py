from .utils import decode_bytes_to_str, encode_str_to_bytes, zero_pad, zero_terminate


class IntBitField:
    def __init__(self, bit_length: int, value: int, bit_offset: int):
        self.bit_length = bit_length
        self.bit_offset = bit_offset
        self.value = value


class StrBitField:
    def __init__(self, byte_array: bytes, bit_offset: int):
        self.byte_length = len(byte_array)
        self.bit_offset = bit_offset
        self.byte_array = byte_array

    @property
    def value(self) -> str:
        return zero_terminate(decode_bytes_to_str(self.byte_array))

    @value.setter
    def value(self, string: str):
        self.byte_array = zero_pad(encode_str_to_bytes(string), self.byte_length)


class IntByteField:
    def __init__(self, byte_length: int, value: int, byte_offset: int):
        self.byte_length = byte_length
        self.byte_offset = byte_offset
        self.value = value


class StrByteField:
    def __init__(self, byte_array: bytes, byte_offset: int):
        self.byte_length = len(byte_array)
        self.byte_offset = byte_offset
        self.byte_array = byte_array

    @property
    def value(self) -> str:
        return zero_terminate(decode_bytes_to_str(self.byte_array))

    @value.setter
    def value(self, string: str):
        self.byte_array = zero_pad(encode_str_to_bytes(string), self.byte_length)
