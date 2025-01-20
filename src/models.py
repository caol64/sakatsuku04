from dataclasses import dataclass

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
    year: int
    month: int
    date: int
    day: int
    money: int
    club_info: list[int]

    def play_date(self):
        return f"{self.year - 2003}年目{self.month}月{self.date}日"

    def money_str(self):
        return f"{self.money}万"

    def __repr__(self):
        return f"""
        Club(
            date={self.play_date()},
            money='{self.money_str()}',
            club_info='{decode_bytes_to_str(bytes(self.club_info))}'
        )"""

    def print_info(self):
        print(self)

@dataclass
class PlayerAbility:
    name: str
    current: int
    current_max: int
    max: int

    def __repr__(self):
        return f"{self.name}: {self.current}|{self.current_max}|{self.max}"

class MyPlayer:
    id: int
    age: int
    no: int
    name: str
    saved_name: list[int]
    abilities: list[PlayerAbility]

    def __init__(self):
        self.abilities = list()

    def __repr__(self):
        return f"""
        MyPlayer(
            id='{self.id}',
            age='{self.age}',
            name='{self.name}',
            saved_name='{zero_terminate(decode_bytes_to_str(bytes(self.saved_name)))}',
            abilities='{self.abilities}',
        )"""

    def saved_name_str(self):
        return zero_terminate(decode_bytes_to_str(bytes(self.saved_name)))

    def print_info(self):
        print(self)

class MyTeam:
    english_name: list[int]
    oilis_english_name: list[int]
    players: list[MyPlayer]

    def __repr__(self):
        return f"""
        MyTeam(
            english_name='{zero_terminate(decode_bytes_to_str(bytes(self.english_name)))}',
            oilis_english_name='{zero_terminate(decode_bytes_to_str(bytes(self.oilis_english_name)))}',
            players='{self.players}',
        )"""

    def print_info(self):
        print(self)

class Player:
    id: int
    age: int
    ability_graph: int
    no: int
    name: str

    def update_name_from_dict(self):
        if self.id is None:
            return
        hex_id = f"{self.id:04X}"
        if hex_id not in Const.PLAYER_DICT:
            self.name = hex_id
        else:
            self.name = Const.PLAYER_DICT[hex_id]

class OtherTeam:
    id: int
    name: str
    players: list[Player]
    unknown1: int
    friendly: int
    unknown2: int

    def __init__(self):
        self.players = list()

    def __repr__(self):
        return f"OtherTeam(id={self.id}, name='{self.name}', unknown1={self.unknown1}, friendly={self.friendly}, unknown2={self.unknown2})"