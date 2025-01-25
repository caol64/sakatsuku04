import csv
from dataclasses import dataclass

from utils import decode_bytes_to_str, encode_str_to_bytes, get_resource_path, zero_pad, zero_terminate

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

class Header:
    year: int
    month: int
    date: int
    day: int
    club_name: bytes
    club_name1: bytes

    def play_date(self):
        return f"{self.year - 2003}年目{self.month}月{self.day}日"

    def __repr__(self):
        return f"""
        Header(
            date={self.play_date()},
            club_name='{zero_terminate(decode_bytes_to_str(self.club_name))}',
            club_name1='{zero_terminate(decode_bytes_to_str(self.club_name1))}'
        )"""

class Club:
    year: IntBitField
    month: IntBitField
    date: IntBitField
    day: IntBitField
    funds: IntBitField
    manager_name: StrBitField
    club_name: StrBitField

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
            with open(get_resource_path('resource/ability.csv'), 'r', encoding='utf8', newline='') as csvfile:
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
    id: IntBitField
    age: IntBitField
    number: IntBitField
    name: StrBitField
    abilities: list[PlayerAbility]
    born: IntBitField
    abroad_times: IntBitField
    height: IntBitField
    foot: IntBitField
    grow_type: IntBitField
    tone_type: IntBitField
    skill: IntBitField
    test: IntBitField = IntBitField(0, 0, 0)

    def __init__(self):
        self.abilities = list()

    def __repr__(self):
        return f"""
        MyPlayer(
            id='{self.id.value}',
            age='{self.age.value}',
            name='{self.name.value}',
            born='{self.born.value}',
            abroad_times='{self.abroad_times.value}',
            height='{self.height.value}',
            number='{self.number.value}',
            foot='{self.foot.value}',
            tone_type='{self.tone_type.value}',
            skill='{self.skill.value}',
            test='{self.test.value}',
        )"""

    def print_info(self):
        print(self)

class MyTeam:
    english_name: StrBitField
    oilis_english_name: StrBitField
    players: list[MyPlayer]

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
class Player:
    id: IntBitField
    age: IntBitField
    ability_graph: IntBitField
    number: IntBitField = None
    _player_dict = None

    @classmethod
    def player_dict(cls) -> list[str]:
        if cls._player_dict is None:
            cls._player_dict = dict()
            with open(get_resource_path('resource/players.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 2:
                        key, value = row
                        cls._player_dict[key] = value
        return cls._player_dict

    @property
    def name(self) -> str:
        if self.id.value is None:
            return ''
        hex_id = f"{self.id.value:04X}"
        if hex_id not in Player.player_dict():
            return hex_id
        else:
            return Player.player_dict()[hex_id]


@dataclass
class OtherTeam:
    index: int
    id: IntBitField
    friendly: IntBitField
    unknown1: IntBitField
    unknown2: IntBitField
    players: list[Player]
    _team_list = None

    @classmethod
    def team_list(cls) -> list[str]:
        if cls._team_list is None:
            cls._team_list = list()
            with open(get_resource_path('resource/teams.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 1:
                        cls._team_list.append(row[0])
        return cls._team_list

    @property
    def name(self) -> str:
        return OtherTeam.team_list()[self.index]
