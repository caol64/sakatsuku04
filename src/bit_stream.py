from utils import ints_to_fixed_bytes


class InputBitStream:
    def __init__(self, input_data: bytes):
        self.input_data = input_data
        self.bit_offset = 0
        self.bit_lengths_list = list()
        self.total_bytes_list = list()
        self.unpacked_list = list()

    def read_bits(self, bits_to_read: int) -> int:
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
        return value

    def unpack_bits(self, bit_lengths: list[int], total_bytes: int = 0) -> list[int]:
        """
        Unpacks a sequence of bits from a byte array based on specified bit lengths.

        Parameters:
            bit_lengths (list[int]): A list of integers specifying the number of bits to unpack for each value.

        Returns:
            list[int]: A list of unpacked integer values.
        """
        if total_bytes == 0:
            total_bytes = int(sum(bit_lengths) / 8)
        result = []  # List to store unpacked values.

        for bits_to_read in bit_lengths:
            result.append(self.read_bits(bits_to_read))
        self.bit_lengths_list.append(bit_lengths)
        self.total_bytes_list.append(total_bytes)
        self.unpacked_list.append(result)
        return result

    def output_buffer(self) -> bytearray:
        out_buffer = bytearray() # Buffer for storing output
        for unpacked, bit_lengths, total_bytes in zip(self.unpacked_list, self.bit_lengths_list, self.total_bytes_list):
            out_buffer += ints_to_fixed_bytes(unpacked, bit_lengths, total_bytes)
        return out_buffer

    def skip(self, bit_offset: int, total_bytes: int):
        self.bit_offset = bit_offset
        self.bit_lengths_list.append([0])
        self.total_bytes_list.append(total_bytes)
        self.unpacked_list.append([0])

    def align(self, total_bytes: int):
        self.bit_lengths_list.append([0])
        self.total_bytes_list.append(total_bytes)
        self.unpacked_list.append([0])

    def seek(self, bit_offset: int):
        self.bit_offset = bit_offset

    def export(self, path: str):
        with open(path, "wb") as f:
            f.write(self.output_buffer())


class OutputBitStream:
    def __init__(self, input_data: list[int]):
        self.input_data = input_data

class BitStream:
    def __init__(self, byte_val: bytes):
        self.byte_val = byte_val
        self.mask = 0x80
        self.offset = 0
        self.current_byte = 0
        self.out_buffer = bytearray() # Buffer for storing output

    def batch_read(self, elements: list[int]):
        for element in elements:
            self.bit_read(element)

    def bit_read(self, bit_count: int) -> int:
        if bit_count == 0:
            return
        sign_extend = False
        if bit_count < 0: # 需要符号扩展
            bit_count *= -1
            sign_extend = True
        bytecount = (bit_count + 7) // 8
        bits = self.mf_read_bits(bit_count)
        mask = (1 << bit_count) - 1
        bits = bits & mask
        if sign_extend:
            # 检查最高位是否为 1
            if bits & (1 << (bit_count - 1)):
                # 扩展高位为 1
                bits |= ~mask
                bits &= ((1 << (bytecount * 8)) - 1)
        self.out_buffer += bits.to_bytes(bytecount, byteorder="little")
        return bits

    def bit_read_str(self, bit_count: int) -> bytearray:
        if bit_count > 0:
            start = len(self.out_buffer)
            while bit_count > 0:
                self.bit_read(8)
                bit_count -= 1
            return self.out_buffer[start:len(self.out_buffer)]

    def mf_read_bits(self, bit_count: int) -> int:
        result = 0
        while bit_count > 0:
            if self.mask == 0x80:
                self.current_byte = self.byte_val[self.offset]
                self.offset += 1
            if self.current_byte & self.mask:
                result = (result << 1) | 1
            else:
                result <<= 1
            self.mask >>= 1
            bit_count -= 1
            if self.mask == 0:
                self.mask = 0x80
        return result

    def align(self, bit_count: int):
        size = len(self.out_buffer)
        bytecount = (bit_count + 7) // 8
        if size % bytecount > 0:
            self.out_buffer.extend(b'\x00' * (bytecount - size % bytecount))

    def alloc(self, n: int):
        self.out_buffer.extend(b'\x00' * n)

    def skip(self, offset: int, mask: int):
        self.offset = offset
        if offset > 0:
            self.current_byte = self.byte_val[offset - 1]
        self.mask = mask