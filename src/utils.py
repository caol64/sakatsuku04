import codecs

from const import Const

def decode_bytes_to_str(byte_array: bytes) -> str:
    if Const.CN_VER:
        return decode_cn(byte_array)
    else:
        return decode_sjis(byte_array)


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