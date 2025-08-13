from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

from .objs import Coach, Player, Scout
from .utils import calc_abil_eval, calc_apos_eval, calc_def, calc_gk, calc_grow_eval, calc_off, calc_phy, calc_sta, calc_sys, calc_tac, find_badden_match, handle_cond, is_album_player, lv_to_dot
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
    team_status: int = 0

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
    kan: int
    moti: int
    power: int
    super_sub: int
    wild_type: int
    weak_type: int
    tired_type: int
    pop: int
    comp: list[int]
    tired: int
    status: int
    condition: int
    explosion_exp: int
    explosion_level: int
    explo_countdown: int
    explo_pending_reason: int
    explo_final_reason: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        current_abils = [f.current for f in self.abilities]
        current_max_abils = [f.current_max for f in self.abilities]
        max_abils = [f.max for f in self.abilities]
        return [
            calc_off(current_abils),
            calc_gk(current_abils) if self.pos == 0 else calc_def(current_abils),
            calc_sta(current_abils),
            calc_phy(current_abils),
            calc_sys(current_abils),
            calc_tac(current_abils),
            calc_off(current_max_abils),
            calc_gk(current_max_abils) if self.pos == 0 else calc_def(current_max_abils),
            calc_sta(current_max_abils),
            calc_phy(current_max_abils),
            calc_sys(current_max_abils),
            calc_tac(current_max_abils),
            calc_off(max_abils),
            calc_gk(max_abils) if self.pos == 0 else calc_def(max_abils),
            calc_sta(max_abils),
            calc_phy(max_abils),
            calc_sys(max_abils),
            calc_tac(max_abils),
        ]

    @computed_field
    @property
    def odc(self) -> list[int]:
        current_abils = [f.current for f in self.abilities]
        return [
            lv_to_dot(calc_off(current_abils)),
            lv_to_dot(calc_gk(current_abils) if self.pos == 0 else calc_def(current_abils))
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
    ability_graph: Optional[int] = None
    number: int
    name: str
    rank: int
    pos: int
    born: int
    cooperation_type: int
    tone_type: int
    style: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    team_index: Optional[int] = None

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def scouts(self) -> Optional[list[str]]:
        scouts_ids = constants.scout_excl_reversed.get(self.id)
        if scouts_ids:
            return [Scout.name(f) for f in scouts_ids]
        return []


class SearchDto(BaseDto):
    name: Optional[str] = None
    pos: Optional[int] = None
    age: Optional[int] = None
    country: Optional[int] = None
    rank: Optional[int] = None
    tone: Optional[int] = None
    cooperation: Optional[int] = None
    team_id: Optional[int] = None
    style: Optional[int] = None
    scout_action: Optional[int] = None

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
    town_type: int


class ScoutDto(BaseDto):
    id: int
    name: str
    abilities: Optional[list[int]] = None
    exclusive_players: Optional[list[SearchDto]] = None
    simi_exclusive_players: Optional[list[SearchDto]] = None


class AbroadCond(BaseDto):
    id: int
    cond: Optional[list[str | int]]

class AbroadDto(BaseDto):
    id: int
    is_enabled: Optional[bool] = None
    cond: Optional[AbroadCond] = None
    abr_up: Optional[list[int]] = None
    abr_uprate: Optional[list[int]] = None
    abr_days: int = 0

    @classmethod
    def get_abr_camp_teams(cls, type: int) -> list['AbroadDto']:
        results = []
        for item in constants.abr_camp_base[type]:
            dto = AbroadDto(id=item[0])
            results.append(dto)
        return results

    @classmethod
    def get_abr_camp_dto(cls, index: int, type: int) -> list['AbroadDto']:
        item = constants.abr_camp_base[type][index]
        dto = AbroadDto(id=item[0])
        dto.abr_up = list(constants.abr_camp_up[type][index])
        dto.abr_uprate = list(constants.abr_camp_uprate[type][index])
        dto.abr_days = item[3]
        cond_id = item[1] >> 4
        cond_val = handle_cond(item[4: 14])
        if type == 1:
            abr_up = dto.abr_up
            keep_indices = [0x29, 0x2A, 0x26, 0x24, 0x25, 0x1c, 0x1d]
            kept = [abr_up[i] for i in keep_indices]
            del abr_up[28:54]
            abr_up.extend(kept)
            abr_up.extend([0xc, 10, 0xc, 10])

        if cond_id == 1 or cond_id == 4:
            dto.cond = AbroadCond(id=cond_id, cond=[])
        elif cond_id == 5:
            dto.cond = AbroadCond(id=cond_id, cond=[Player(f).name for f in cond_val])
        elif cond_id == 6:
            dto.cond = AbroadCond(id=cond_id, cond=[Coach.name(f + 20000) for f in cond_val])
        elif cond_id == 7 or  cond_id == 3 or cond_id == 2:
            dto.cond = AbroadCond(id=cond_id, cond=cond_val)
        return dto

class BPlayerDto(BaseDto):
    id: int = 0
    name: str
    born: int
    pos: int
    age: int
    rank: int
    tone_type: int
    cooperation_type: int
    wave_type: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    abilities: list[int] = [0] * 64
    height: int
    style: int
    super_sub: int
    wild_type: int
    weak_type: int
    tired_type: int
    pop: int
    desire: int
    pride: int
    ambition: int
    patient: int
    persistence: int
    foot: int
    debut_year: int
    signing_difficulty: int
    sp_comment: Optional[str] = None

    @computed_field
    @property
    def abil_eval(self) -> int:
        return calc_abil_eval([r for r in self.abilities][0: 36], self.pos)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        return [
            calc_off(self.abilities),
            calc_gk(self.abilities) if self.pos == 0 else calc_def(self.abilities),
            calc_sta(self.abilities),
            calc_phy(self.abilities),
            calc_sys(self.abilities),
            calc_tac(self.abilities),
        ]

    @computed_field
    @property
    def odc(self) -> list[int]:
        return [
            lv_to_dot(calc_off(self.abilities)),
            lv_to_dot(calc_gk(self.abilities) if self.pos == 0 else calc_def(self.abilities))
        ]

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        return calc_apos_eval(self.abilities)

    @computed_field
    @property
    def badden_players(self) -> Optional[list[str]]:
        badden_ids = find_badden_match(self.id)
        return [Player(p).name for p in badden_ids] if badden_ids else None

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

class SimpleBPlayerDto(BaseDto):
    id: int
    name: str
    pos: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def scouts(self) -> Optional[list[str]]:
        scouts_ids = constants.scout_excl_reversed.get(self.id)
        if scouts_ids:
            return [Scout.name(f) for f in scouts_ids]
        return []
