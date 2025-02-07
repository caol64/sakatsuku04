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
            with open(get_resource_path('resource/players.csv'), 'r', encoding='utf8', newline='') as csvfile:
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
    index: int
    id: IntBitField
    age: IntBitField
    number: IntBitField
    name: StrBitField
    abilities: list[PlayerAbility]
    born: IntBitField
    abroad_times: IntBitField
    abroad_days: IntBitField
    height: IntBitField
    foot: IntBitField
    grow_type: IntBitField
    tone_type: IntBitField
    skill: IntBitField
    magic_value: IntBitField
    test: IntBitField = IntBitField(0, 0, 0)
    un: list[int]
    player: Player

    @property
    def prefer_foot(self) -> int:
        if self.foot.value == 0:
            return '左脚'
        elif self.foot.value == 1:
            return '右脚'
        else:
            return '双脚'

    def __init__(self, index: int):
        self.index = index
        self.abilities = list()
        self.un = list()

    def set_player(self):
        self.player = Player(self.id.value)

    def __repr__(self):
        return f"""
        MyPlayer(
            id='{self.id.value}',
            age='{self.age.value}',
            name='{self.name.value}',
            born='{self.born.value}',
            abroad_times='{self.abroad_times.value}',
            abroad_days='{self.abroad_days.value}',
            height='{self.height.value}',
            number='{self.number.value}',
            foot='{self.foot.value}',
            tone_type='{self.tone_type.value}',
            skill='{self.skill.value}',
            test='{self.test.value}',
            un='{self.un}',
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
    order_list = ["GK", "CDF", "SDF", "DMF", "SMF", "OMF", "FW"]

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

    @property
    def sorted_players(self) -> list[OtherPlayer]:
        return sorted(self.players, key=self.sort_key)

    def sort_key(self, player: OtherPlayer):
        if player.player and player.player.pos:
            return self.order_list.index(player.player.pos)
        else:
            return -1