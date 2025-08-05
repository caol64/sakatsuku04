import csv
import json
from typing import Optional

from .io import CnVer
from .utils import get_resource_path



class Player:
    _player_dict: Optional[dict] = None
    _player_comments_dict: Optional[dict] = None

    def __init__(self, id: int):
        self.id = id
        if id in Player.player_dict():
            self._player_properties = Player.player_dict()[id]
        else:
            self._player_properties = {}

    @classmethod
    def player_dict(cls) -> dict[int, list[str]]:
        if cls._player_dict is None:
            cls._player_dict = dict()
            file = ("bplayers_zh18.csv" if CnVer.is_i8 else "bplayers_zh.csv") if CnVer.is_cn else "bplayers_jp.csv"
            with open(get_resource_path(file), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    cls._player_dict[i] = row
        return cls._player_dict

    @classmethod
    def player_comments_dict(cls) -> dict[int, str]:
        if cls._player_comments_dict is None:
            cls._player_comments_dict = dict()
            file = ("sp_comments_zh18.json" if CnVer.is_i8 else "sp_comments_zh.json") if CnVer.is_cn else "sp_comments_jp.json"
            with open(get_resource_path(file), 'r', encoding='utf8', newline='') as f:
                cls._player_comments_dict = json.load(f)
        return cls._player_comments_dict

    @classmethod
    def reset_player_dict(cls):
        cls._player_dict = None
        cls._player_comments_dict = None

    @property
    def name(self) -> str:
        return self._player_properties[0] if self._player_properties else ''

    @property
    def pos(self) -> int:
        return self._player_properties[1] if self._player_properties else 0

    @property
    def rank(self) -> int:
        return self._player_properties[2] if self._player_properties else 0

    @property
    def cooperation_type(self) -> int:
        return self._player_properties[3] if self._player_properties else 0

    @property
    def tone_type(self) -> int:
        return self._player_properties[4] if self._player_properties else 0

    @property
    def grow_type_phy(self) -> int:
        return self._player_properties[5] if self._player_properties else 0

    @property
    def grow_type_tec(self) -> int:
        return self._player_properties[6] if self._player_properties else 0

    @property
    def grow_type_sys(self) -> int:
        return self._player_properties[7] if self._player_properties else 0

    @property
    def born(self) -> int:
        return self._player_properties[8] if self._player_properties else 0

    @property
    def style(self) -> int:
        return self._player_properties[9] if self._player_properties else 0

    @property
    def sp_comment(self) -> Optional[str]:
        return Player.player_comments_dict().get(str(self.id), None)


class Scout:
    _scout_dict: Optional[dict] = None

    @classmethod
    def scout_dict(cls) -> dict[int, list[str]]:
        if cls._scout_dict is None:
            cls._scout_dict = dict()
            file = "bscouts_zh.csv" if CnVer.is_cn else "bscouts_jp.csv"
            with open(get_resource_path(file), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    cls._scout_dict[i + 30000] = row
        return cls._scout_dict

    @classmethod
    def reset_scout_dict(cls):
        cls._scout_dict = None

    @classmethod
    def name(cls, id: int) -> str:
        return cls.scout_dict().get(id)[0]


class Coach:
    _coach_dict: Optional[dict] = None

    @classmethod
    def coach_dict(cls) -> dict[int, list[str]]:
        if cls._coach_dict is None:
            cls._coach_dict = dict()
            file = "bcoachs_zh.csv" if CnVer.is_cn else "bcoachs_jp.csv"
            with open(get_resource_path(file), 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    cls._coach_dict[i + 20000] = row
        return cls._coach_dict

    @classmethod
    def reset_coach_dict(cls):
        cls._coach_dict = None

    @classmethod
    def name(cls, id: int) -> str:
        return cls.coach_dict().get(id)[0]
