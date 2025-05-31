import codecs
import csv
import importlib.resources
from pathlib import Path


def decode_bytes_to_str(byte_array: bytes) -> str:
    if CnVersion.CN_VER:
        return decode_cn(byte_array)
    else:
        return decode_sjis(byte_array)

def encode_str_to_bytes(string: str) -> bytes:
    if CnVersion.CN_VER:
        return encode_cn(string)
    else:
        return encode_sjis(string)


def zero_terminate(data: str) -> str:
    """
    Truncate a string at the first NUL ('\0') character, if any.
    """
    i = data.find('\0')
    if i == -1:
        return data
    return data[:i]

def zero_pad(data: bytes, target_length: int) -> bytes:
    padding_length = target_length - len(data)
    if padding_length > 0:
        padding = b'\x00' * padding_length
        return data + padding
    elif padding_length == 0:
        return data
    else:
        return data[:target_length]

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

def encode_sjis(s: str) -> bytes:
    """Encode a string to bytes using the Shift-JIS encoding."""
    try:
        return codecs.encode(s, "shift-jis", "replace")
    except Exception as ex:
        print(ex)
        return b""

def decode_cn(s: bytes) -> str:
    decoded_str = []
    code_map = CnVersion.get_char_dict()
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

def encode_cn(s: str) -> bytes:
    encoded_bytes = bytearray()
    code_map_reversed = {v: k for k, v in CnVersion.get_char_dict.items()} # 反转字典，方便查找
    for char in s:
        if char in code_map_reversed:
            encoded_bytes.extend(bytes.fromhex(code_map_reversed[char]))
        elif ord(char) < 128: # 只处理ASCII字符，其他字符忽略或者抛出异常
            encoded_bytes.append(ord(char))
        else:
            print(f"Character {char} not in code map, ignored.")
            #raise ValueError(f"Character {char} not in code map") # 也可以抛出异常
    return bytes(encoded_bytes)


def get_resource_path(relative_path) -> Path:
    with importlib.resources.path("sakatsuku04.resource", relative_path) as file_path:
        return file_path
    # if hasattr(sys, "_MEIPASS"):
    #     # 打包环境：资源文件位于 _MEIPASS 指定的临时目录
    #     return Path(sys._MEIPASS).resolve() / relative_path
    # else:
    #     # 开发环境：资源文件位于当前脚本所在的目录
    #     return Path(__file__).resolve().parent.parent / relative_path


def convert_rank(rank: int) -> str:
    rank_dict = {
        0: 'SSS',
        1: 'SS',
        2: 'S',
        3: 'A',
        4: 'B',
        5: 'C',
        6: 'D',
        7: 'E',
        8: 'F',
        9: 'G',
        10: 'H',
    }
    return rank_dict.get(rank)


class CnVersion:
    CN_VER = False
    _cn_char_dict = None

    @classmethod
    def get_char_dict(cls) -> dict[str, str]:
        if cls._cn_char_dict is None:
            cls._cn_char_dict = {}
            with open(get_resource_path('cn.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 2:
                        key, value = row
                        cls._cn_char_dict[key] = value
        return cls._cn_char_dict
