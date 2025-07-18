from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

from .objs import Player
from .utils import calc_abil_eval, calc_apos_eval, calc_grow_eval, find_badden_match, is_album_player, ability_to_lv, lv_to_dot
from . import constants


class BaseDto(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ClubDto(BaseDto):
    club_name: str
    year: int
    month: int
    date: int
    day: int
    funds_high: int
    funds_low: int
    manager_name: str
    difficulty: int
    seed: int

    def combo_funds(self) -> int:
        return self.funds_high * 10000 + self.funds_low


class MyTeamPlayerDto(BaseDto):
    id: int
    name: str
    pos: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)


class PlayerAbilityDto(BaseDto):
    index: int
    current: int
    current_max: int
    max: int


class MyPlayerDto(BaseDto):
    index: int
    id: int
    age: int
    number: int
    name: str
    born: int
    abroad_times: int
    height: int
    foot: int
    rank: int
    pos: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    tone_type: int
    cooperation_type: int
    style: int
    abilities: list[PlayerAbilityDto]
    desire: int
    pride: int
    ambition: int
    patient: int
    persistence: int
    grow_type_id: int
    sp_comment: Optional[str]
    salary_high: int
    salary_low: int
    offer_years_passed: int
    offer_years_total: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        return [
            calc_off(self),
            calc_gk(self) if self.pos == 0 else calc_def(self),
            calc_sta(self),
            calc_phy(self),
            calc_sys(self),
            calc_tac(self),
            calc_off(self, 1),
            calc_gk(self, 1) if self.pos == 0 else calc_def(self, 1),
            calc_sta(self, 1),
            calc_phy(self, 1),
            calc_sys(self, 1),
            calc_tac(self, 1),
            calc_off(self, 2),
            calc_gk(self, 2) if self.pos == 0 else calc_def(self, 2),
            calc_sta(self, 2),
            calc_phy(self, 2),
            calc_sys(self, 2),
            calc_tac(self, 2),
        ]

    @computed_field
    @property
    def odc(self) -> list[int]:
        return [
            lv_to_dot(calc_off(self)),
            lv_to_dot(calc_gk(self) if self.pos == 0 else calc_def(self))
        ]

    @computed_field
    @property
    def abil_eval(self) -> int:
        return calc_abil_eval([r.current for r in self.abilities][0: 36], self.pos)

    @computed_field
    @property
    def grow_eval(self) -> int:
        return calc_grow_eval(self.grow_type_tec, self.age)

    @computed_field
    @property
    def max_abil_eval(self) -> int:
        return calc_abil_eval([r.max for r in self.abilities][0: 36], self.pos)

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        return calc_apos_eval([r.current for r in self.abilities])

    @computed_field
    @property
    def badden_players(self) -> Optional[list[str]]:
        badden_ids = find_badden_match(self.id)
        return [Player(p).name for p in badden_ids] if badden_ids else None

    def combo_salary(self) -> int:
        return (self.salary_high * 10000 + self.salary_low) // 100

    @computed_field
    @property
    def phy_grows(self) -> list[int]:
        return list(constants.tbl_phy_grow_type[self.grow_type_phy])

    @computed_field
    @property
    def tec_grows(self) -> list[int]:
        return list(constants.tbl_tec_grow_type[self.grow_type_tec])

    @computed_field
    @property
    def sys_grows(self) -> list[int]:
        return list(constants.tbl_sys_grow_type[self.grow_type_sys])


class TeamDto(BaseDto):
    index: int
    name: str
    friendly: int


class OtherTeamPlayerDto(BaseDto):
    id: int
    age: int
    ability_graph: int
    number: int
    name: str
    rank: int
    pos: int
    born: int
    cooperation_type: int
    tone_type: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    team_index: Optional[int] = None

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)


class SearchDto(BaseDto):
    name: Optional[str] = None
    pos: Optional[int] = None
    age: Optional[int] = None
    country: Optional[int] = None
    rank: Optional[int] = None
    tone: Optional[int] = None
    cooperation: Optional[int] = None

class TownDto(BaseDto):
    living: int
    economy: int
    sports: int
    env: int
    population: int
    price: int
    traffic_level: int
    soccer_pop: int
    soccer_level: int


def _calc_avg(player: MyPlayerDto, indices: tuple[int], mode: int) -> int:
    total = 0
    count = 0
    for i in indices:
        ability = player.abilities[i]
        if mode == 0:
            lv = ability_to_lv(ability.current)
        elif mode == 1:
            lv = ability_to_lv(ability.current_max)
        elif mode == 2:
            lv = ability_to_lv(ability.max)
        else:
            raise ValueError(f"Invalid mode: {mode}")
        total += lv
        count += 1
    return total // count if count else 0


def calc_off(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_off, mode)

def calc_def(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_def, mode)

def calc_gk(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_gk, mode)

def calc_phy(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_phy, mode)

def calc_sys(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_sys, mode)

def calc_tac(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_tac, mode)

def calc_sta(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, constants.abi_sta, mode)
