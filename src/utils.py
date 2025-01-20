import codecs

from const import Const

def decode_bytes_to_str(byte_val: bytes) -> str:
    if Const.CN_VER:
        return decode_cn(byte_val)
    else:
        return decode_sjis(byte_val)


def zero_terminate(s: str) -> str:
    """
    Truncate a string at the first NUL ('\0') character, if any.
    """
    i = s.find('\0')
    if i == -1:
        return s
    return s[:i]


def decode_name(byte_array: bytes) -> str:
    """Decode bytes to a string."""
    return byte_array.decode("ascii")


def decode_sjis(s: bytes) -> str:
    """Decode bytes to a string using the Shift-JIS encoding."""
    try:
        return codecs.decode(s, "shift-jis", "replace").replace("\u3000", " ")
    except Exception as ex:
        print(ex)
        return "\uFFFD" * 3

def decode_cn(s: bytes) -> str:
    """
    Decode a byte sequence using a custom code map (Const.CN_DICT).
    Bytes not in the code map are treated as ASCII characters.
    """
    decoded_str = []
    code_map = Const.CN_DICT
    i = 0
    length = len(s)
    
    while i < length:
        # Check if there are at least 2 bytes remaining for a valid chunk
        if i + 1 < length:
            chunk = s[i:i + 2].hex().upper()
            if chunk in code_map:
                decoded_str.append(code_map[chunk])
                i += 2
                continue
        
        # Default: treat as an ASCII character
        decoded_str.append(chr(s[i]))
        i += 1
    
    return ''.join(decoded_str)

def unpack_bits(data: bytes, bit_lengths: list[int]) -> list[int]:
    """
    Unpacks a sequence of bits from a byte array based on specified bit lengths.

    Parameters:
        data (bytes): The input byte array containing packed bits.
        bit_lengths (list[int]): A list of integers specifying the number of bits to unpack for each value.

    Returns:
        list[int]: A list of unpacked integer values.
    """
    result = []  # List to store unpacked values.
    bit_offset = 0  # The current bit offset in the input data.

    for bits_to_read in bit_lengths:
        value = 0  # The value being unpacked.
        remaining_bits = bits_to_read

        while remaining_bits > 0:
            # Calculate the current byte index and bit position within the byte.
            byte_index = bit_offset // 8
            bit_index = bit_offset % 8

            # Ensure we don't exceed the data length.
            if byte_index >= len(data):
                raise ValueError("Bit lengths exceed the size of the input data.")

            # Determine how many bits can be read from the current byte.
            bits_in_current_byte = min(8 - bit_index, remaining_bits)

            # Extract the relevant bits from the current byte.
            current_byte = data[byte_index]
            mask = (1 << bits_in_current_byte) - 1  # Mask to extract the desired bits.
            value <<= bits_in_current_byte  # Shift value to make room for new bits.
            value |= (current_byte >> (8 - bit_index - bits_in_current_byte)) & mask

            # Update offsets and remaining bits to process.
            bit_offset += bits_in_current_byte
            remaining_bits -= bits_in_current_byte

        result.append(value)

    return result


def pack_bits(values: list[int], bit_lengths: list[int]) -> bytes:
    """
    Packs a sequence of integers into a byte array based on specified bit lengths.

    Parameters:
        values (list[int]): A list of integers to be packed.
        bit_lengths (list[int]): A list of integers specifying the number of bits to use for each value.
    """

    result = bytearray()  # Byte array to store the packed data.
    current_byte = 0  # The current byte being filled.
    bits_filled = 0  # Number of bits filled in the current byte.

    for value, bits in zip(values, bit_lengths):
        # Ensure the value fits in the specified number of bits.
        if value >= (1 << bits):
            raise ValueError(f"Value {value} cannot be represented in {bits} bits.")

        while bits > 0:
            # Calculate how many bits can be written to the current byte.
            remaining_bits_in_byte = 8 - bits_filled
            bits_to_write = min(bits, remaining_bits_in_byte)

            # Extract and write the bits to the current byte.
            current_byte <<= bits_to_write
            current_byte |= (value >> (bits - bits_to_write)) & ((1 << bits_to_write) - 1)

            bits_filled += bits_to_write
            bits -= bits_to_write

            # If the current byte is full, append it to the result and reset.
            if bits_filled == 8:
                result.append(current_byte)
                current_byte = 0
                bits_filled = 0

    # If there are remaining bits in the last byte, pad and append it.
    if bits_filled > 0:
        current_byte <<= (8 - bits_filled)  # Left-align remaining bits.
        result.append(current_byte)

    return bytes(result)

def ints_to_fixed_bytes(int_array: list[int], bit_lengths: list[int], total_bytes: int = 8) -> bytes:
    """
    Converts a list of integers into a fixed-length byte array of `total_bytes` size.

    Parameters:
        int_array (list[int]): List of integers to convert.
        bit_lengths (list[int]): A list of integers specifying the number of bits to use for each value.
        total_bytes (int): Total length of the resulting byte array (default is 8).
    """
    byte_result = bytearray()  # Initialize a mutable byte array.

    # Convert each integer into bytes (little-endian, n bytes per integer).
    for int_value, bit_length in zip(int_array, bit_lengths):
        if bit_length > 0:
            byte_result.extend(int_value.to_bytes((bit_length + 7) // 8, byteorder='little', signed=False))
        elif bit_length == 0:
            byte_result.extend(b'\x00' * total_bytes)
        else:
            byte_result.extend(int_value.to_bytes((bit_length * -1 + 7) // 8, byteorder='little', signed=False))

    # Adjust the size to `total_bytes`:
    if len(byte_result) < total_bytes:
        # Pad with zeros if the result is smaller than `total_bytes`.
        byte_result.extend(b'\x00' * (total_bytes - len(byte_result)))
    elif len(byte_result) > total_bytes:
        # Truncate if the result is larger than `total_bytes`.
        byte_result = byte_result[:total_bytes]

    return bytes(byte_result)