from .models import IntBitField, StrBitField


class InputBitStream:
    def __init__(self, input_data: bytes, debug_mode: bool = False):
        self.input_data = input_data
        self.bit_offset = 0
        self.unpacked_bytes_length = 0
        self.debug_mode = debug_mode
        if debug_mode:
            self.unpacked_bytes = bytearray()

    def read_bits(self, bits_to_read: int, sign_extend: bool = False) -> int:
        value = 0  # The value being unpacked.
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
        return value

    def unpack_bits(self, bit_lengths: int | list[int], total_bytes: int = 0) -> IntBitField | list[IntBitField]:
        result_is_int = False
        if isinstance(bit_lengths, int):
            bit_lengths = [bit_lengths]
            result_is_int = True
        if total_bytes == 0:
            total_bytes = (sum(bit_lengths) + 7) // 8

        result = list()
        sum_bytes = 0

        for bits_to_read in bit_lengths:
            if bits_to_read < 0:
                bits_to_read *= -1
                sign_extend = True
            else:
                sign_extend = False
            byte_length = (bits_to_read + 7) // 8
            bit_offset = self.bit_offset
            unpacked_int = self.read_bits(bits_to_read, sign_extend)
            result.append(IntBitField(bits_to_read, unpacked_int, bit_offset))
            if self.debug_mode:
                self.unpacked_bytes.extend(unpacked_int.to_bytes(byte_length, 'little'))
                sum_bytes += byte_length

        if self.debug_mode:
            if sum_bytes < total_bytes:
                self.unpacked_bytes.extend([0] * (total_bytes - sum_bytes))
            if total_bytes > 0 and sum_bytes > total_bytes:
                self.unpacked_bytes = self.unpacked_bytes[:total_bytes - sum_bytes]
        self.unpacked_bytes_length += total_bytes

        return result if not result_is_int else result[0]

    def unpack_str(self, total_bytes: int) -> StrBitField:
        result = bytearray()
        bit_offset = self.bit_offset
        for _ in range(total_bytes):
            unpacked_int = self.read_bits(8)
            unpacked_bytes = unpacked_int.to_bytes(1, 'little')
            result.extend(unpacked_bytes)
        if self.debug_mode:
            self.unpacked_bytes.extend(result)
        self.unpacked_bytes_length += total_bytes

        return StrBitField(bytes(result), bit_offset)

    def skip(self, bit_offset: int, total_bytes: int):
        self.bit_offset = bit_offset
        if self.debug_mode:
            self.unpacked_bytes.extend([0] * total_bytes)
        self.unpacked_bytes_length += total_bytes

    def align(self, total_bytes: int):
        if self.debug_mode:
            self.unpacked_bytes.extend([0] * total_bytes)
        self.unpacked_bytes_length += total_bytes

    def seek(self, bit_offset: int):
        self.bit_offset = bit_offset

    def export(self, path: str):
        if self.debug_mode:
            with open(path, "wb") as f:
                f.write(self.unpacked_bytes)

    def padding(self, data: bytes):
        if self.debug_mode:
            self.unpacked_bytes.extend(data)
        self.unpacked_bytes_length += len(data)

class OutputBitStream:
    def __init__(self, input_data: bytes):
        self.input_data = input_data

    def write_bits(self, bits_length: int, bits_value: int, bit_offset: int):
        remaining_bits = bits_length
        current_offset = bit_offset
        output_data = bytearray(self.input_data)

        while remaining_bits > 0:
            # Calculate the current byte index and bit position within the byte.
            byte_index = current_offset // 8
            bit_index = current_offset % 8

            # Determine how many bits can be written to the current byte.
            bits_in_current_byte = min(8 - bit_index, remaining_bits)

            # Mask to isolate the bits to write in the current byte.
            mask = (1 << bits_in_current_byte) - 1
            bits_to_write = (bits_value >> (remaining_bits - bits_in_current_byte)) & mask

            # Clear the target bits in the current byte.
            clear_mask = ~(mask << (8 - bit_index - bits_in_current_byte))
            output_data[byte_index] &= clear_mask

            # Write the new bits to the current byte.
            output_data[byte_index] |= bits_to_write << (8 - bit_index - bits_in_current_byte)

            # Update offsets and remaining bits to process.
            current_offset += bits_in_current_byte
            remaining_bits -= bits_in_current_byte
        self.input_data = bytes(output_data)

    def pack_bits(self, bit_field: IntBitField | StrBitField) -> bytes:
        if isinstance(bit_field, IntBitField):
            self.write_bits(bit_field.bit_length, bit_field.value, bit_field.bit_offset)
        else:
            for i in range(bit_field.byte_length):
                self.write_bits(8, bit_field.byte_array[i], bit_field.bit_offset + i * 8)

    def export(self, path: str):
        with open(path, "wb") as f:
            f.write(self.input_data)
