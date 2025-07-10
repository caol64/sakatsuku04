import codecs
import csv
import importlib.resources
from pathlib import Path
from typing import Optional

team_ids = (
    2, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270,
    271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285,
    286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300,
    301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315,
    316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330,
    331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345,
    346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360,
    361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375,
    376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390,
    391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405,
    406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420,
    421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435,
    436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450,
    451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465,
    466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480,
    481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495,
    496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510,
    511, 512, 513, 514, 515, 516, 517, 518, 519
)

album_players = (
    7382, 7383, 7384, 7385, 7386, 7387, 7388, 7389, 7390, 7391, 9774, 9775, 9776,
    7392, 7393, 7394, 7395, 7396, 7397, 7410, 7411, 7412, 7413, 7398, 7399, 7400,
    7401, 7402, 7403, 7404, 7405, 7406, 7407, 7408, 7409, 7414, 7415, 7416, 7417,
    7418, 7419, 7420, 7421, 7422, 7423, 7424, 7425, 7426, 7427, 7428, 7429, 7430,
    7431, 7432, 7433, 7434, 7435, 7436, 7437, 7438, 7439, 7440, 7441, 7442, 7443,
    7444, 7445, 7446, 7447, 7448, 9777, 9778, 9779, 9780, 9781, 9782, 9783, 9784,
    9785, 9786, 9787, 9788, 9789, 9790, 9791, 9792, 9793, 9794, 9795, 9796, 9797,
    9798, 9799, 9800, 9801, 9802, 9803, 9804, 9805, 9806, 9807, 9808, 9809, 9810,
    9811, 7449, 7450, 7451, 7452, 7453, 7454, 7455, 7456, 7457, 7458, 7459, 7460,
    7461, 7462, 7463, 7464, 7465, 7466, 7467, 7468, 7469, 7470, 7471, 7472, 7473,
    7474, 7475, 7476, 7477, 7478, 7479, 7480, 7481, 7482, 7483, 7484, 7485, 7486,
    7487, 7488, 7489, 7490, 7491, 7492, 7493, 7494, 7495, 7496, 7497, 7498, 7499,
    7500, 7501, 7502, 7503, 7504, 7505, 7506, 7507, 7508, 7509, 7510, 7511, 7512,
    7513, 7514, 7515, 7516, 7517, 7518, 7519, 7520, 7521, 7522, 7523, 7524, 7525,
    7526, 7527, 7528, 7529, 7530, 7531, 7532, 7533, 7534, 7535, 7536, 7537, 7538,
    7539, 7540, 7541, 7235, 7542, 7546, 7544, 7545, 7549, 7543, 7547, 7548, 7550,
    7551, 7552, 7553, 7555, 7557, 7554, 7560, 7556, 7559, 7558, 7562, 7563, 7561,
    7564, 7575, 7565, 7567, 7572, 7566, 7573, 7574, 7569, 7571, 7570, 7568, 7576,
    7578, 7577, 7580, 7579, 7581, 7582, 7583, 7585, 7584, 7586, 7587, 7588, 7590,
    7593, 7589, 7592, 7591, 7595, 7596, 7594, 7597, 7599, 7598, 7600, 7603, 7602,
    7601, 7607, 7604, 7606, 7605, 7608, 9764, 9763, 9765, 9766, 9767, 9769, 9768,
    9771, 9770, 9772, 9773
)


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

def get_cn_char_dict() -> dict[str, str]:
    global _cn_char_dict
    if _cn_char_dict is None:
        _cn_char_dict = get_jp_char_dict().copy()
        _cn_char_dict.update(_load_char_dict('cn.csv'))
    return _cn_char_dict

def decode_bytes_to_str(byte_array: bytes, is_cn = False) -> str:
    return decode(byte_array, get_cn_char_dict()) if is_cn else decode(byte_array, get_jp_char_dict())

def encode_str_to_bytes(string: str, is_cn = False) -> bytes:
    return encode(string, get_cn_char_dict()) if is_cn else encode(string, get_jp_char_dict())


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


def get_resource_path(relative_path) -> Path:
    with importlib.resources.path("sakatsuku04.resource", relative_path) as file_path:
        return file_path


def is_album_player(id: int) -> bool:
    return id in album_players
