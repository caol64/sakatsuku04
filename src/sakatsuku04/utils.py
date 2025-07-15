import codecs
import csv
import importlib.resources
from pathlib import Path
from typing import Optional

from . import constants


_cn_char_dict: Optional[dict[str, str]] = None
_jp_char_dict: Optional[dict[str, str]] = None

def _load_char_dict(filename: str) -> dict[str, str]:
    result = {}
    with open(get_resource_path(filename), 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                key, value = row
                result[key] = value
    return result

def get_jp_char_dict() -> dict[str, str]:
    global _jp_char_dict
    if _jp_char_dict is None:
        _jp_char_dict = _load_char_dict('jp.csv')
    return _jp_char_dict

def get_cn_char_dict(is_18: bool) -> dict[str, str]:
    global _cn_char_dict
    if _cn_char_dict is None:
        _cn_char_dict = get_jp_char_dict().copy()
        path = 'cn18.csv' if is_18 else 'cn.csv'
        _cn_char_dict.update(_load_char_dict(path))
    return _cn_char_dict

def decode_bytes_to_str(byte_array: bytes, is_cn = False, is_18 = False) -> str:
    return decode(byte_array, get_cn_char_dict(is_18)) if is_cn else decode(byte_array, get_jp_char_dict())

def encode_str_to_bytes(string: str, is_cn = False, is_18 = False) -> bytes:
    return encode(string, get_cn_char_dict(is_18)) if is_cn else encode(string, get_jp_char_dict())


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
        return s.decode("shift-jis", errors="replace")
    except UnicodeDecodeError as ex:
        print(ex)
        return "?"

def encode_sjis(s: str) -> bytes:
    """Encode a string to bytes using the Shift-JIS encoding."""
    try:
        return codecs.encode(s, "shift-jis", "replace")
    except Exception as ex:
        print(ex)
        return b""


def decode(s: bytes, char_dict: dict[str, str]) -> str:
    if s == b"\xea\x52\xea\x53\xea\x54\xea\x55\xea\x56\xea\x57":
        return "ｼｭﾅｲﾀﾞｰ 潤之助"
    if s == b"\xea\x40\xea\x41\xea\x42\xea\x43\xea\x44\xea\x45":
        return "ﾃﾞﾋﾞｯﾄﾞｿﾝ 純 ﾏｰｶｽ"
    if s == b"\xea\x58\xea\x59\xea\x5a\xea\x5b\xea\x5c\xea\x5d":
        return "田中 ﾏﾙｸｽ闘莉王"
    if s == b"\xea\x46\xea\x47\xea\x48\xea\x49\xea\x4a\xea\x4b":
        return "三都主 ｱﾚｻﾝﾄﾞﾛ"
    decoded_str = []
    i = 0
    length = len(s)

    while i < length:
        # Check if there are at least 2 bytes remaining for a valid chunk
        if i + 1 < length:
            chunk = s[i:i + 2].hex().upper()
            if chunk in char_dict:
                decoded_str.append(char_dict[chunk])
                i += 2
                continue

        chunk = s[i:i + 1].hex().upper()
        if chunk in char_dict:
            decoded_str.append(char_dict[chunk])
            i += 1
            continue
        # Default: treat as an ASCII character
        decoded_str.append(decode_sjis(s[i:i+1]))
        i += 1

    return ''.join(decoded_str)

def encode(s: str, char_dict: dict[str, str]) -> bytes:
    encoded_bytes = bytearray()
    code_map_reversed = {v: k for k, v in char_dict.items()} # 反转字典，方便查找
    for char in s:
        if char in code_map_reversed:
            encoded_bytes.extend(bytes.fromhex(code_map_reversed[char]))
        elif ord(char) < 128: # 只处理ASCII字符，其他字符忽略或者抛出异常
            encoded_bytes.append(ord(char))
        else:
            print(f"Character {char} not in code map, ignored.")
            #raise ValueError(f"Character {char} not in code map") # 也可以抛出异常
    return bytes(encoded_bytes)


def get_resource_path(relative_path: str) -> Path:
    with importlib.resources.path("sakatsuku04.resource", relative_path) as file_path:
        return file_path


def is_album_player(id: int) -> bool:
    return id in constants.album_players


def find_name_matches(players: dict, name: str) -> list[id]:
    result = []
    for id, value in players.items():
        if name in value[0]:
            result.append(id)
    return result


def player_hexagon_convert(input_value: int) -> int:
    return (min(input_value + 10, 90) * 100) // 90


def lv_to_dot(level_value: float) -> int:
    return (min((level_value * 95) // 90 + 5, 100) * 32) // 100


def ability_to_lv(exp: int) -> int:
    level, loop_limit = (1, 0x32) if exp < 16776 else (0x33, 0x65)
    while level <= loop_limit:
        level += 1
        if constants.exp_to_lv[level] >= exp:
            break
    return level - 1


def calc_abil_eval(abilities: list[int], pos: int) -> int:
    total = 0
    for i, a in enumerate(abilities):
        total += ability_to_lv(a) * constants.status_table_abil[i][pos]
    for i in range(8):
        if total // 15 <= constants.status_table_mes[i]:
            return i
    return 7
