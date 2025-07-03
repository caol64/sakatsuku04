import csv
from .utils import get_resource_path


class Position:
    ITEMS = {
        0: "GK",
        1: "CDF",
        2: "SDF",
        3: "DMF",
        4: "SMF",
        5: "OMF",
        6: "FW",
        7: "WING",
    }

    ITEMS_REVERSE = { value: key for key, value in ITEMS.items() }


class Rank:
    ITEMS = {
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
    def cooperation_type(self) -> str:
        return self._player_properties[4] if self._player_properties else ''

    @property
    def tone_type(self) -> str:
        return self._player_properties[5] if self._player_properties else ''

    @property
    def grow_type_phy(self) -> str:
        return self._player_properties[6] if self._player_properties else ''

    @property
    def grow_type_tec(self) -> str:
        return self._player_properties[7] if self._player_properties else ''

    @property
    def grow_type_sys(self) -> str:
        return self._player_properties[8] if self._player_properties else ''


class Scout:
    _scout_dict = None

    @classmethod
    def scout_dict(cls) -> dict[str, str]:
        if cls._scout_dict is None:
            cls._scout_dict = dict()
            with open(get_resource_path('scouts.csv'), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    cls._scout_dict[row[0]] = row[1]
        return cls._scout_dict

    @classmethod
    def name(cls, id: str) -> str:
        return Scout.scout_dict().get(id)
