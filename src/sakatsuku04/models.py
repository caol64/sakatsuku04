import csv
from dataclasses import dataclass

from .utils import convert_rank, decode_bytes_to_str, encode_str_to_bytes, get_resource_path, zero_pad, zero_terminate

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

class Header:
    u1: IntByteField
    u2: IntByteField
    year: IntByteField
    month: IntByteField
    date: IntByteField
    day: IntByteField
    club_name: StrByteField
    club_name1: StrByteField

    @property
    def play_date(self):
        return f"{self.year.value - 2003}年目{self.month.value}月{self.day.value}日"

    def __repr__(self):
        return f"""
        Header(
            date={self.play_date},
            club_name='{self.club_name.value}',
            club_name1='{self.club_name1.value}'
        )"""


class Position:
    _position_dict = None

    @classmethod
    def position_dict(cls) -> dict[str, str]:
        if cls._position_dict is None:
            cls._position_dict = dict()
            with open(get_resource_path('position.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._position_dict[row[0]] = row[1]
        return cls._position_dict

    @classmethod
    def position_dict_reverse(cls) -> dict[str, int]:
        return {value: int(key, 16) for key, value in cls.position_dict().items()}


class Player:
    _player_dict = None

    def __init__(self, id: int):
        self.id = id
        hex_id = f"{self.id:04X}"
        if hex_id in Player.player_dict():
            self._player_properties = Player.player_dict()[hex_id]
        else:
            self._player_properties = {}

    @classmethod
    def player_dict(cls) -> dict[str, list[str]]:
        if cls._player_dict is None:
            cls._player_dict = dict()
            with open(get_resource_path('players.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._player_dict[row[0]] = row
        return cls._player_dict

    @property
    def name(self) -> str:
        return self._player_properties[2] if self._player_properties else ''

    @property
    def rank(self) -> str:
        return self._player_properties[1] if self._player_properties else ''

    @property
    def pos(self) -> str:
        return self._player_properties[3] if self._player_properties else ''

    @property
    def team_work(self) -> str:
        return self._player_properties[4] if self._player_properties else ''

    @property
    def tone_type(self) -> str:
        return self._player_properties[5] if self._player_properties else ''

    @property
    def grow_type_phy(self) -> str:
        return self._player_properties[6] if self._player_properties else ''

    @property
    def grow_type_tech(self) -> str:
        return self._player_properties[7] if self._player_properties else ''

    @property
    def grow_type_sys(self) -> str:
        return self._player_properties[8] if self._player_properties else ''

class Club:
    year: IntBitField
    month: IntBitField
    date: IntBitField
    day: IntBitField
    funds: IntBitField
    manager_name: StrBitField
    club_name: StrBitField
    difficulty: IntBitField

    @property
    def funds_high(self) -> int:
        return self.funds.value // 10000

    @property
    def funds_low(self) -> int:
        return self.funds.value % 10000

    def set_funds(self, hign: int, low: int):
        self.funds.value = hign * 10000 + low

    def get_play_date(self) -> str:
        return f"{self.year.value - 2003}年目{self.month.value}月{self.date.value}日"

    def get_formated_funds(self) -> str:
        yi = self.funds_high
        wan = self.funds_low
        if yi > 0 and wan > 0:
            return f"{yi}亿{wan}万"
        elif yi > 0:
            return f"{yi}亿"
        else:
            return f"{wan}万"

    def __repr__(self):
        return f"""
        Club(
            date={self.get_play_date()},
            funds='{self.get_formated_funds()}',
            manager_name='{self.manager_name.value}',
            club_name='{self.club_name.value}'
        )"""

    def print_info(self):
        print(self)


@dataclass
class PlayerAbility:
    index: int
    current: IntBitField
    current_max: IntBitField
    max: IntBitField
    _ablility_list = None

    @classmethod
    def ablility_list(cls) -> list[str]:
        if cls._ablility_list is None:
            cls._ablility_list = list()
            with open(get_resource_path('ability.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 1:
                        cls._ablility_list.append(row[0])
        return cls._ablility_list

    @property
    def name(self) -> str:
        return PlayerAbility.ablility_list()[self.index]

    def __repr__(self):
        return f"{self.name}: {self.current.value}|{self.current_max.value}|{self.max.value}"

class MyPlayer:
    index: int
    id: IntBitField
    age: IntBitField
    number: IntBitField
    name: StrBitField
    abilities: list[PlayerAbility]
    born: IntBitField
    born2: IntBitField
    abroad_times: IntBitField
    abroad_days: IntBitField
    height: IntBitField
    foot: IntBitField
    rank: IntBitField
    pos: IntBitField
    pos2: IntBitField
    grow_type_phy: IntBitField
    grow_type_tec: IntBitField
    grow_type_bra: IntBitField
    tone_type: IntBitField
    cooperation_type: IntBitField
    style: IntBitField
    style_equip: IntBitField
    style_learned1: IntBitField
    style_learned2: IntBitField
    style_learned3: IntBitField
    style_learned4: IntBitField
    magic_value: IntBitField
    test: IntBitField = IntBitField(0, 0, 0)
    un: list[int]

    @property
    def prefer_foot(self) -> int:
        if self.foot.value == 0:
            return '左脚'
        elif self.foot.value == 1:
            return '右脚'
        else:
            return '双脚'

    @property
    def readable_rank(self) -> str:
        return convert_rank(self.rank.value)

    @property
    def readable_style(self) -> str:
        hex_id = f"{self.style.value:02X}"
        return Style.style_dict()[hex_id]

    @property
    def readable_born(self) -> str:
        hex_id = f"{self.born.value:02X}"
        return Region.region_dict()[hex_id]

    @property
    def readable_cooperation_type(self) -> str:
        hex_id = f"{self.cooperation_type.value:02X}"
        return CooperationType.cooperation_type_dict()[hex_id]

    @property
    def readable_pos(self) -> str:
        hex_id = f"{self.pos.value:02X}"
        return Position.position_dict()[hex_id]

    @property
    def readable_tone_type(self) -> str:
        hex_id = f"{self.tone_type.value:02X}"
        return ToneType.tone_type_dict()[hex_id]

    def get_readable_grow_type(self, grow_type: int) -> str:
        hex_id = f"{grow_type:02X}"
        return GrowType.grow_type_dict()[hex_id]

    def __init__(self, index: int):
        self.index = index
        self.abilities = list()
        self.un = list()

    def set_style(self, style_index: int):
        new_int = (self.style_learned2.value << 32) | self.style_learned1.value
        new_int |= (1 << style_index)
        self.style_learned1.value = new_int & 0xFFFFFFFF
        self.style_learned2.value = (new_int >> 32) & 0xFFFFFFFF

    def __repr__(self):
        return f"""
        MyPlayer(
            id='{self.id.value}',
            name='{self.name.value}',
        )"""

    def print_info(self):
        print(self)

class MyTeam:
    english_name: StrBitField
    oilis_english_name: StrBitField
    players: list[MyPlayer]
    my_scouts: list['Scout']
    scout_candidates: list['Scout']
    _sort_keys = list(Position.position_dict().values())

    @property
    def sorted_players(self) -> list[MyPlayer]:
        return sorted(self.players, key=self.sort_key)

    def sort_key(self, player: MyPlayer):
        if player.pos:
            return self._sort_keys.index(player.readable_pos)
        else:
            return -1

    def __repr__(self):
        return f"""
        MyTeam(
            english_name='{self.english_name.value}',
            oilis_english_name='{self.oilis_english_name.value}',
            players='{self.players}',
        )"""

    def print_info(self):
        print(self)

@dataclass
class OtherPlayer:
    id: IntBitField
    age: IntBitField
    ability_graph: IntBitField
    number: IntBitField = None

    def __post_init__(self):
        if self.id.value is not None:
            self.player = Player(self.id.value)


@dataclass
class OtherTeam:
    index: int
    id: IntBitField
    friendly: IntBitField
    unknown1: IntBitField
    unknown2: IntBitField
    players: list[OtherPlayer]
    _team_list = None
    _sort_keys = list(Position.position_dict().values())

    @classmethod
    def team_list(cls) -> list[str]:
        if cls._team_list is None:
            cls._team_list = list()
            with open(get_resource_path('teams.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 1:
                        cls._team_list.append(row[0])
        return cls._team_list

    @property
    def name(self) -> str:
        return OtherTeam.team_list()[self.index]

    @property
    def sorted_players(self) -> list[OtherPlayer]:
        return sorted(self.players, key=self.sort_key)

    def sort_key(self, player: OtherPlayer):
        if player.player and player.player.pos:
            return self._sort_keys.index(player.player.pos)
        else:
            return -1


@dataclass
class Scout:
    id: IntBitField
    age: IntBitField
    saved_name: StrBitField = None
    abilities: list[IntBitField] = None
    offer_years: IntBitField = None
    area1: IntBitField = None
    area2: IntBitField = None
    _ablility_list = None
    _scout_dict = None

    def __post_init__(self):
        hex_id = f"{self.id.value:04X}"
        self.name = Scout.scout_dict().get(hex_id)

    @classmethod
    def ablility_list(cls) -> list[str]:
        if cls._ablility_list is None:
            cls._ablility_list = list()
            with open(get_resource_path('scout_ability.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 1:
                        cls._ablility_list.append(row[0])
        return cls._ablility_list

    @classmethod
    def scout_dict(cls) -> dict[str, str]:
        if cls._scout_dict is None:
            cls._scout_dict = dict()
            with open(get_resource_path('scouts.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._scout_dict[row[0]] = row[1]
        return cls._scout_dict


class Region:
    _region_dict = None

    @classmethod
    def get_region(cls, code: int) -> str:
        hex_id = f"{code:02X}"
        return cls.region_dict()[hex_id]

    @classmethod
    def region_dict(cls) -> dict[str, str]:
        if cls._region_dict is None:
            cls._region_dict = dict()
            with open(get_resource_path('regions.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._region_dict[row[0]] = row[1]
        return cls._region_dict

    @classmethod
    def region_dict_reverse(cls) -> dict[str, int]:
        return {value: int(key, 16) for key, value in cls.region_dict().items()}


class GrowType:
    _grow_type_dict = None

    @classmethod
    def grow_type_dict(cls) -> dict[str, str]:
        if cls._grow_type_dict is None:
            cls._grow_type_dict = dict()
            with open(get_resource_path('grow_type.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._grow_type_dict[row[0]] = row[2]
        return cls._grow_type_dict

    @classmethod
    def grow_type_dict_reverse(cls) -> dict[str, int]:
        return {value: int(key, 16) for key, value in cls.grow_type_dict().items()}


class CooperationType:
    _cooperation_type_dict = None

    @classmethod
    def cooperation_type_dict(cls) -> dict[str, str]:
        if cls._cooperation_type_dict is None:
            cls._cooperation_type_dict = dict()
            with open(get_resource_path('cooperation_type.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._cooperation_type_dict[row[0]] = row[1]
        return cls._cooperation_type_dict

    @classmethod
    def cooperation_type_dict_reverse(cls) -> dict[str, int]:
        return {value: int(key, 16) for key, value in cls.cooperation_type_dict().items()}


class ToneType:
    _tone_type_dict = None

    @classmethod
    def tone_type_dict(cls) -> dict[str, str]:
        if cls._tone_type_dict is None:
            cls._tone_type_dict = dict()
            with open(get_resource_path('tone_type.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._tone_type_dict[row[0]] = row[1]
        return cls._tone_type_dict

    @classmethod
    def tone_type_dict_reverse(cls) -> dict[str, int]:
        return {value: int(key, 16) for key, value in cls.tone_type_dict().items()}


class Style:
    _style_dict = None

    @classmethod
    def style_dict(cls) -> dict[str, str]:
        if cls._style_dict is None:
            cls._style_dict = dict()
            with open(get_resource_path('styles.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._style_dict[row[0]] = row[1]
        return cls._style_dict

    @classmethod
    def style_dict_reverse(cls) -> dict[str, int]:
        return {value: int(key, 16) for key, value in cls.style_dict().items()}
