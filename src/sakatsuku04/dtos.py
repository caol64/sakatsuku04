from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

from .objs import Coach, Player, Scout
from .utils import calc_abil_eval, calc_apos_eval, calc_def, calc_gk, calc_grow_eval, calc_mhex_sys, calc_off, calc_phy, calc_sta, calc_sys, calc_tac, find_badden_match, get_rank_to_number, handle_cond, is_album_player, lv_to_dot, sabil_2_apt, mcoach_eval
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
    wave_type: int
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
    abilities: list[int]
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
    unlock_year: int
    signing_difficulty: int

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

    @computed_field
    @property
    def sp_comment(self) -> str:
        player = Player(self.id)
        sp_comment = player.sp_comment
        if sp_comment:
            return sp_comment
        index = self.rank // 2 * 8 if self.rank < 10 else 32
        if self.age < constants.bplayer_eval_age_threshold[self.grow_type_tec]:
            return Player.player_eval_list()[index]
        else:
            return Player.player_eval_list()[index + 40]

    @computed_field
    @property
    def grow_eval(self) -> int:
        if Player(self.id).sp_comment:
            return 0
        return calc_grow_eval(self.grow_type_tec, self.age)

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


class SimpleBScoutDto(BaseDto):
    id: int
    name: str


class SimpleBCoachDto(BaseDto):
    id: int
    name: str


class BScoutDto(BaseDto):
    id: int = 0
    name: str
    born: int
    abilities: list[int]
    nati1: int
    nati2: int
    age: int
    rank: int
    salary_high: int
    salary_low: int
    signing_difficulty: int
    ambition: int
    persistence: int

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        return [
            (self.abilities[2] + self.abilities[4]) // 2,
            (self.abilities[3] + self.abilities[4] + self.abilities[5]) // 3,
            (self.abilities[1] + self.abilities[3]) // 2,
            (self.abilities[1] + self.abilities[2]) // 2,
        ]

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        return [
            sabil_2_apt(self.abilities[constants.epos_to_pos[constants.apos_to_epos[i]] + 0x11])
            for i in range(11)
        ]

    @computed_field
    @property
    def exclusive_players(self) -> list[str]:
        return [Player(f).name for f in constants.scout_excl_tbl.get(self.id, [])]

    @computed_field
    @property
    def simi_exclusive_players(self) -> list[str]:
        return [Player(f).name for f in constants.scout_simi_excl_tbl.get(self.id, [])]

    @computed_field
    @property
    def eval(self) -> str:
        plus = 2
        if constants.scout_excl_tbl.get(self.id) is not None:
            plus = 0
        comment = Scout.scout_comments_list()[get_rank_to_number(self.rank) * 8 + plus]
        return comment

class BCoachDto(BaseDto):
    id: int = 0
    name: str
    born: int
    age: int
    abilities: list[int]
    rank: int
    salary_high: int
    salary_low: int
    signing_difficulty: int
    styles: list[int]
    coach_type: int
    desire: int
    ambition: int
    persistence: int
    activate_plan: int
    training_plan: int
    training_strength: int
    ac_sp_practice1: int
    ac_sp_practice2: int

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        tac_sum = self.abilities[25] + self.abilities[26] + self.abilities[27]
        tac_max = max([self.abilities[25], self.abilities[26], self.abilities[27]])
        tac_avg = (tac_sum - tac_max) // 27
        return [
            self.abilities[10],
            self.abilities[11],
            ((self.abilities[28] + self.abilities[29]) * 250 + (tac_max * 6 + tac_avg * 4) * 50) // 1000,
            calc_mhex_sys(self.abilities),
            (self.abilities[1] + self.abilities[2] + self.abilities[3]) // 3,
            (self.abilities[0] + self.abilities[2]) // 2,
        ]

    @computed_field
    @property
    def eval(self) -> str:
        plus = 0
        rank = get_rank_to_number(self.rank)
        if constants.mcoach_skill.get(self.id - 20000) is not None:
            plus = constants.mcoach_skill.get(self.id - 20000)
            return Coach.mcoach_comments_list()[rank * 10 + plus]
        eval_tuple = mcoach_eval(self.abilities)
        index = constants.mcoach_eval_rank_abil_mapping.get(rank)[eval_tuple[1]][eval_tuple[0]]
        comment = Coach.mcoach_comments_list()[index - 700]
        return comment

    @computed_field
    @property
    def sp_skill(self) -> Optional[int]:
        return constants.mcoach_skill.get(self.id - 20000)

    @computed_field
    @property
    def coach_type_cnv(self) -> int:
        return constants.coach_mapping[self.coach_type]
