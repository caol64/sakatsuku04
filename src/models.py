from dataclasses import dataclass

from bit_stream import IntBitField, StrBitField
from const import Const
from utils import decode_bytes_to_str, zero_terminate

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
    name: str
    current: IntBitField
    current_max: IntBitField
    max: IntBitField

    def __repr__(self):
        return f"{self.name}: {self.current.value}|{self.current_max.value}|{self.max.value}"

class MyPlayer:
    id: IntBitField
    age: IntBitField
    number: IntBitField
    name: StrBitField
    abilities: list[PlayerAbility]
    index: int

    def __init__(self):
        self.abilities = list()

    def __repr__(self):
        return f"""
        MyPlayer(
            id='{self.id.value}',
            age='{self.age.value}',
            name='{self.name.value}',
            abilities='{self.abilities}',
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

class Player:
    id: IntBitField
    age: IntBitField
    ability_graph: IntBitField
    number: IntBitField

    @property
    def name(self) -> str:
        if self.id.value is None:
            return ''
        hex_id = f"{self.id.value:04X}"
        if hex_id not in Const.PLAYER_DICT:
            return hex_id
        else:
            return Const.PLAYER_DICT[hex_id]


class OtherTeam:
    id: IntBitField
    name: str
    players: list[Player]
    unknown1: IntBitField
    friendly: IntBitField
    unknown2: IntBitField

    def __init__(self):
        self.players = list()
