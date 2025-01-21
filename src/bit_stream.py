from utils import decode_bytes_to_str, zero_terminate


class InputBitStream:
    def __init__(self, input_data: bytes):
        self.input_data = input_data
        self.bit_offset = 0
        self.unpacked_bytes = bytearray()

    def read_bits(self, bits_to_read: int) -> tuple[int, int]:
        value = 0  # The value being unpacked.
        sign_extend = False
        if bits_to_read < 0:
            bits_to_read *= -1
            sign_extend = True
        remaining_bits = bits_to_read

        while remaining_bits > 0:
            # Calculate the current byte index and bit position within the byte.
            byte_index = self.bit_offset // 8
            bit_index = self.bit_offset % 8

            # Determine how many bits can be read from the current byte.
            bits_in_current_byte = min(8 - bit_index, remaining_bits)

            # Extract the relevant bits from the current byte.
            current_byte = self.input_data[byte_index]
            mask = (1 << bits_in_current_byte) - 1  # Mask to extract the desired bits.
            value <<= bits_in_current_byte  # Shift value to make room for new bits.
            value |= (current_byte >> (8 - bit_index - bits_in_current_byte)) & mask

            # Update offsets and remaining bits to process.
            self.bit_offset += bits_in_current_byte
            remaining_bits -= bits_in_current_byte

        if sign_extend:
            # 检查最高位是否为 1
            if value & (1 << (bits_to_read - 1)):
                value |= ~mask
                value &= ((1 << ((bits_to_read + 7) // 8 * 8)) - 1)
        byte_length = (bits_to_read + 7) // 8
        return value, byte_length

    def unpack_bits(self, bit_lengths: list[int], total_bytes: int = 0) -> list['IntBitField']:
        """
        Unpacks a sequence of bits from a byte array based on specified bit lengths.

        Parameters:
            bit_lengths (list[int]): A list of integers specifying the number of bits to unpack for each value.
            total_bytes (int): Optional; the total number of bytes expected (default is auto-calculated).

        Returns:
            bytes: The unpacked bits as a bytes object.
        """
        if total_bytes == 0:
            total_bytes = (sum(bit_lengths) + 7) // 8

        result = list()
        sum_bytes = 0

        for bits_to_read in bit_lengths:
            unpacked_int, byte_length = self.read_bits(bits_to_read)
            result.append(IntBitField(bits_to_read, unpacked_int))
            self.unpacked_bytes.extend(unpacked_int.to_bytes(byte_length, 'little'))
            sum_bytes += byte_length

        if sum_bytes < total_bytes:
            self.unpacked_bytes.extend([0] * (total_bytes - sum_bytes))
        
        return result

    def unpack_str(self, total_bytes: int) -> 'StrBitField':
        result = bytearray()
        for _ in range(total_bytes):
            unpacked_int, _ = self.read_bits(8)
            unpacked_bytes = unpacked_int.to_bytes(1, 'little')
            result.extend(unpacked_bytes)
        self.unpacked_bytes.extend(result)

        return StrBitField(bytes(result))

    def skip(self, bit_offset: int, total_bytes: int):
        self.bit_offset = bit_offset
        self.unpacked_bytes.extend([0] * total_bytes)

    def align(self, total_bytes: int):
        self.unpacked_bytes.extend([0] * total_bytes)

    def seek(self, bit_offset: int):
        self.bit_offset = bit_offset

    def export(self, path: str):
        with open(path, "wb") as f:
            f.write(self.unpacked_bytes)


class IntBitField:
    def __init__(self, bit_length: int, value: int):
        self.bit_length = bit_length
        self.bit_offset = 0
        self.value = value


class StrBitField:
    def __init__(self, byte_array: bytes):
        self.byte_length = len(byte_array)
        self.bit_length = self.byte_length * 8
        self.bit_offset = 0
        self.byte_array = byte_array

    @property
    def value(self) -> str:
        return zero_terminate(decode_bytes_to_str(self.byte_array))